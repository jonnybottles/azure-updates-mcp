"""Get previews tool for tracking Azure preview features."""

from ..feeds.azure_rss import fetch_updates


async def get_previews(
    limit: int = 20,
    category: str | None = None,
) -> list[dict]:
    """Get Azure preview features for testing and adoption planning.

    Args:
        limit: Maximum number of results to return (default: 20, max: 100).
        category: Optional category filter (case-insensitive partial match).

    Returns:
        List of preview updates sorted by publication date.
    """
    # Clamp limit to reasonable bounds
    limit = max(1, min(limit, 100))

    updates = await fetch_updates()

    results = []
    for update in updates:
        # Filter for "In preview" status
        if not update.status or update.status.lower() != "in preview":
            continue

        # Check category filter if provided
        if category:
            category_lower = category.lower()
            category_match = any(
                category_lower in cat.lower() for cat in update.categories
            )
            if not category_match:
                continue

        results.append(update.to_dict())

        if len(results) >= limit:
            break

    return results
