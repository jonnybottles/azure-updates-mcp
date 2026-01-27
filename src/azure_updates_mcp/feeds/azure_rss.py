"""Azure Updates RSS feed fetching and parsing."""

import re
from datetime import datetime
from email.utils import parsedate_to_datetime

import feedparser
import httpx

from ..models.update import AzureUpdate

AZURE_UPDATES_RSS_URL = "https://www.microsoft.com/releasecommunications/api/v2/azure/rss"

# Status patterns that appear in titles like "[Launched]", "[In preview]"
STATUS_PATTERN = re.compile(r"\[(Launched|In preview|In development|Retirements?)\]", re.IGNORECASE)

# Known status categories from the feed
STATUS_CATEGORIES = {"launched", "in preview", "in development", "retirements"}


async def fetch_updates() -> list[AzureUpdate]:
    """Fetch and parse Azure Updates from the RSS feed.

    Returns:
        List of AzureUpdate objects sorted by publication date (newest first).
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(AZURE_UPDATES_RSS_URL, timeout=30.0)
        response.raise_for_status()

    feed = feedparser.parse(response.text)
    updates = []

    for entry in feed.entries:
        update = _parse_entry(entry)
        if update:
            updates.append(update)

    # Sort by publication date, newest first
    updates.sort(key=lambda u: u.pub_date, reverse=True)
    return updates


def _parse_entry(entry: feedparser.FeedParserDict) -> AzureUpdate | None:
    """Parse a single feed entry into an AzureUpdate.

    Args:
        entry: A feedparser entry dictionary.

    Returns:
        AzureUpdate object or None if parsing fails.
    """
    try:
        # Parse publication date
        pub_date = _parse_date(entry)

        # Get categories and extract status
        categories = [tag.term for tag in getattr(entry, "tags", [])]
        status = _extract_status(entry.get("title", ""), categories)

        return AzureUpdate(
            guid=entry.get("id", entry.get("link", "")),
            title=entry.get("title", ""),
            link=entry.get("link", ""),
            description=entry.get("summary", entry.get("description", "")),
            pub_date=pub_date,
            categories=categories,
            status=status,
        )
    except Exception:
        return None


def _parse_date(entry: feedparser.FeedParserDict) -> datetime:
    """Parse publication date from feed entry.

    Args:
        entry: A feedparser entry dictionary.

    Returns:
        datetime object, defaults to now if parsing fails.
    """
    # Try published first, then updated
    date_str = entry.get("published") or entry.get("updated")
    if date_str:
        try:
            return parsedate_to_datetime(date_str)
        except (ValueError, TypeError):
            pass

    # Try feedparser's parsed time tuple
    time_struct = entry.get("published_parsed") or entry.get("updated_parsed")
    if time_struct:
        try:
            return datetime(*time_struct[:6])
        except (ValueError, TypeError):
            pass

    return datetime.now()


def _extract_status(title: str, categories: list[str]) -> str | None:
    """Extract update status from title or categories.

    Args:
        title: The update title (may contain [Status] tag).
        categories: List of category tags.

    Returns:
        Normalized status string or None.
    """
    # Try to extract from title first
    match = STATUS_PATTERN.search(title)
    if match:
        status = match.group(1)
        # Normalize "Retirements" to "Retirements"
        return status.capitalize() if status.lower() != "in preview" else "In preview"

    # Check categories for status
    for cat in categories:
        cat_lower = cat.lower()
        if cat_lower in STATUS_CATEGORIES:
            if cat_lower == "in preview":
                return "In preview"
            elif cat_lower == "in development":
                return "In development"
            return cat.capitalize()

    return None
