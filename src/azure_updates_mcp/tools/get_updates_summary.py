"""Get updates summary tool for aggregate statistics."""

from collections import Counter

from ..feeds.azure_rss import fetch_updates


async def get_updates_summary() -> dict:
    """Get a dashboard-style overview of Azure updates.

    Returns:
        Dictionary containing:
        - total_updates: Total number of updates
        - by_status: Counts for each status type
        - top_categories: Top 10 categories by update count
        - date_range: Oldest and newest update dates
    """
    updates = await fetch_updates()

    if not updates:
        return {
            "total_updates": 0,
            "by_status": {},
            "top_categories": [],
            "date_range": None,
        }

    # Count by status
    status_counter: Counter[str] = Counter()
    for update in updates:
        status_key = update.status or "Unknown"
        status_counter[status_key] += 1

    # Count categories
    category_counter: Counter[str] = Counter()
    for update in updates:
        for category in update.categories:
            category_counter[category] += 1

    # Get top 10 categories
    top_categories = [
        {"name": name, "count": count}
        for name, count in category_counter.most_common(10)
    ]

    # Date range (updates are sorted newest first)
    newest = updates[0].pub_date
    oldest = updates[-1].pub_date

    return {
        "total_updates": len(updates),
        "by_status": dict(status_counter),
        "top_categories": top_categories,
        "date_range": {
            "oldest": oldest.isoformat(),
            "newest": newest.isoformat(),
        },
    }
