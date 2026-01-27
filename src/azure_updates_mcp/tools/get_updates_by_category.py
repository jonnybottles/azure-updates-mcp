"""Get updates by category tool for filtering by service or area."""

from ..feeds.azure_rss import fetch_updates


async def get_updates_by_category(
    category: str,
    limit: int = 10,
    status: str | None = None,
) -> list[dict]:
    """Filter Azure updates by category with case-insensitive partial matching.

    Args:
        category: Category to filter by (e.g., "AKS" matches "Azure Kubernetes Service (AKS)").
        limit: Maximum number of results to return (default: 10, max: 100).
        status: Optional status filter (Launched, In preview, In development, Retirements).

    Returns:
        List of matching update objects sorted by publication date.
    """
    # Clamp limit to reasonable bounds
    limit = max(1, min(limit, 100))

    updates = await fetch_updates()
    category_lower = category.lower()

    results = []
    for update in updates:
        # Check status filter if provided
        if status and update.status:
            if update.status.lower() != status.lower():
                continue
        elif status and not update.status:
            continue

        # Check if any category matches (case-insensitive partial match)
        category_match = any(
            category_lower in cat.lower() for cat in update.categories
        )
        if category_match:
            results.append(update.to_dict())

        if len(results) >= limit:
            break

    return results
