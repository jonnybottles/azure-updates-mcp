"""Get two-week summary tool for category-grouped Azure updates."""

from collections import Counter
from datetime import datetime, timedelta

from ..feeds.azure_rss import fetch_updates


async def get_two_week_summary(weeks: int = 2, highlight_count: int = 10) -> dict:
    """Get a structured summary of Azure updates from the last N weeks.

    Returns category-grouped summary with status counts and highlighted updates.

    Args:
        weeks: Number of weeks to look back (default: 2, range: 1-12).
        highlight_count: Number of highlighted updates to include (default: 10, max: 50).

    Returns:
        Dictionary containing:
        - period: Start date, end date, and number of weeks
        - total_count: Total number of updates in the period
        - by_status: Counts for each status type
        - by_category: List of categories with counts and status breakdowns
        - highlights: Most recent N updates with details
    """
    # Clamp parameters to reasonable bounds
    weeks = max(1, min(weeks, 12))
    highlight_count = max(1, min(highlight_count, 50))

    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(weeks=weeks)

    updates = await fetch_updates()

    # Filter updates within date range (updates are sorted newest first)
    filtered = []
    for update in updates:
        # Make comparison date timezone-naive
        pub_dt = update.pub_date.replace(tzinfo=None)
        if start_date <= pub_dt <= end_date:
            filtered.append(update)

    if not filtered:
        return {
            "period": {
                "start": start_date.strftime("%Y-%m-%d"),
                "end": end_date.strftime("%Y-%m-%d"),
                "weeks": weeks,
            },
            "total_count": 0,
            "by_status": {},
            "by_category": [],
            "highlights": [],
        }

    # Aggregate by status
    by_status: Counter[str] = Counter()
    for update in filtered:
        status_key = update.status or "Unknown"
        by_status[status_key] += 1

    # Aggregate by category with status breakdown
    category_data: dict[str, dict] = {}
    for update in filtered:
        for cat in update.categories:
            if cat not in category_data:
                category_data[cat] = {"count": 0, "statuses": Counter()}
            category_data[cat]["count"] += 1
            category_data[cat]["statuses"][update.status or "Unknown"] += 1

    # Sort categories by count descending
    by_category = sorted(
        [
            {
                "category": cat,
                "count": data["count"],
                "statuses": dict(data["statuses"]),
            }
            for cat, data in category_data.items()
        ],
        key=lambda x: x["count"],
        reverse=True,
    )

    # Get highlights (most recent N updates, already sorted newest first)
    highlights = [
        {
            "title": update.title,
            "link": update.link,
            "status": update.status,
            "date": update.pub_date.strftime("%Y-%m-%d"),
            "categories": update.categories,
        }
        for update in filtered[:highlight_count]
    ]

    return {
        "period": {
            "start": start_date.strftime("%Y-%m-%d"),
            "end": end_date.strftime("%Y-%m-%d"),
            "weeks": weeks,
        },
        "total_count": len(filtered),
        "by_status": dict(by_status),
        "by_category": by_category,
        "highlights": highlights,
    }
