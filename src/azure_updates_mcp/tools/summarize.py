"""Summarize tool for aggregate statistics on Azure Updates."""

from collections import Counter
from datetime import datetime, timedelta

from ..feeds.azure_rss import fetch_updates


async def azure_updates_summarize(
    weeks: int | None = None,
    top_n: int = 10,
) -> dict:
    """Get aggregate statistics and a structured summary of Azure service updates.

    Provides a dashboard-style overview of Azure updates including counts by status,
    top categories, date range information, and recent highlights. Optionally scoped
    to a specific time window.

    Use this tool to:
    - Get an overall snapshot of all available updates (no parameters)
    - Get a summary for the last N weeks (weeks=2 for the past two weeks)
    - Control how many top categories and highlights are shown (top_n=5)

    Args:
        weeks: Optional number of weeks to look back. When omitted, summarizes
            all available updates. Range: 1-12 when provided.
        top_n: Number of top categories and highlighted updates to include
            (default: 10, max: 50).

    Returns:
        Dictionary containing:
        - total_updates: Total number of updates in scope
        - by_status: Counts for each status type (Launched, In preview, etc.)
        - top_categories: Top N categories with counts and status breakdowns
        - date_range: Oldest and newest update dates (and period info if weeks specified)
        - highlights: Most recent N updates with title, link, status, date, categories
    """
    # Clamp top_n
    top_n = max(1, min(top_n, 50))

    updates = await fetch_updates()

    # Apply time window filter if specified
    period_info: dict | None = None
    if weeks is not None:
        weeks = max(1, min(weeks, 12))
        end_date = datetime.now()
        start_date = end_date - timedelta(weeks=weeks)

        updates = [
            u
            for u in updates
            if start_date <= u.pub_date.replace(tzinfo=None) <= end_date
        ]

        period_info = {
            "start": start_date.strftime("%Y-%m-%d"),
            "end": end_date.strftime("%Y-%m-%d"),
            "weeks": weeks,
        }

    if not updates:
        return {
            "total_updates": 0,
            "by_status": {},
            "top_categories": [],
            "date_range": period_info,
            "highlights": [],
        }

    # Count by status
    status_counter: Counter[str] = Counter()
    for update in updates:
        status_counter[update.status or "Unknown"] += 1

    # Count categories with status breakdown
    category_data: dict[str, dict] = {}
    for update in updates:
        for cat in update.categories:
            if cat not in category_data:
                category_data[cat] = {"count": 0, "statuses": Counter()}
            category_data[cat]["count"] += 1
            category_data[cat]["statuses"][update.status or "Unknown"] += 1

    # Sort categories by count descending, take top N
    sorted_categories = sorted(
        category_data.items(),
        key=lambda x: (-x[1]["count"], x[0]),
    )
    top_categories = [
        {
            "category": cat,
            "count": data["count"],
            "statuses": dict(data["statuses"]),
        }
        for cat, data in sorted_categories[:top_n]
    ]

    # Date range (updates are sorted newest first)
    newest = updates[0].pub_date
    oldest = updates[-1].pub_date

    date_range: dict = {
        "oldest": oldest.isoformat(),
        "newest": newest.isoformat(),
    }
    if period_info:
        date_range["period"] = period_info

    # Highlights: most recent N updates
    highlights = [
        {
            "title": update.title,
            "link": update.link,
            "status": update.status,
            "date": update.pub_date.strftime("%Y-%m-%d"),
            "categories": update.categories,
        }
        for update in updates[:top_n]
    ]

    return {
        "total_updates": len(updates),
        "by_status": dict(status_counter),
        "top_categories": top_categories,
        "date_range": date_range,
        "highlights": highlights,
    }
