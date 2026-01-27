"""List categories tool for discovering available Azure service categories."""

from collections import Counter

from ..feeds.azure_rss import fetch_updates


async def list_categories() -> dict:
    """Discover all unique categories from Azure updates with counts.

    Returns:
        Dictionary with 'categories' containing category names and their occurrence counts,
        sorted by count descending.
    """
    updates = await fetch_updates()

    # Count all categories across all updates
    category_counter: Counter[str] = Counter()
    for update in updates:
        for category in update.categories:
            category_counter[category] += 1

    # Sort by count descending, then alphabetically
    sorted_categories = sorted(
        category_counter.items(),
        key=lambda x: (-x[1], x[0]),
    )

    return {
        "total_categories": len(sorted_categories),
        "categories": [{"name": name, "count": count} for name, count in sorted_categories],
    }
