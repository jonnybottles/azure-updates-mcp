"""Category discovery tool for listing available Azure service categories."""

from collections import Counter

import httpx
from fastmcp import Context

from ..feeds.azure_rss import fetch_updates


async def azure_updates_list_categories(ctx: Context) -> dict:
    """List all available categories from Azure updates with occurrence counts.

    Returns every unique category tag found across all updates in the RSS feed,
    sorted by frequency. Use this to discover valid category values before
    filtering with azure_updates_search(category=...).

    Returns:
        Dictionary with:
        - total_categories: Number of unique categories
        - categories: List of objects with 'name' and 'count', sorted by count descending
    """
    try:
        await ctx.info("Fetching Azure updates to extract categories...")
        updates = await fetch_updates()
        await ctx.info(f"Retrieved {len(updates)} updates from feed")
    except httpx.HTTPError as e:
        await ctx.error(f"Failed to fetch updates: {str(e)}")
        return {
            "total_categories": 0,
            "categories": [],
            "error": f"Failed to fetch Azure updates: {str(e)}",
        }

    category_counter: Counter[str] = Counter()
    for update in updates:
        for category in update.categories:
            category_counter[category] += 1

    sorted_categories = sorted(
        category_counter.items(),
        key=lambda x: (-x[1], x[0]),
    )

    return {
        "total_categories": len(sorted_categories),
        "categories": [{"name": name, "count": count} for name, count in sorted_categories],
    }
