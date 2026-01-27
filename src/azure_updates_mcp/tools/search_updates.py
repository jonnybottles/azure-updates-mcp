"""Search updates tool for filtering Azure Updates."""

from ..feeds.azure_rss import fetch_updates


async def search_updates(
    query: str,
    limit: int = 10,
    status: str | None = None,
) -> list[dict]:
    """Search Azure updates by keyword and optional filters.

    Args:
        query: Search term to match against title and description (case-insensitive).
        limit: Maximum number of results to return (default: 10, max: 100).
        status: Optional status filter (Launched, In preview, In development, Retirements).

    Returns:
        List of matching update objects sorted by publication date.
    """
    # Clamp limit to reasonable bounds
    limit = max(1, min(limit, 100))

    updates = await fetch_updates()
    query_lower = query.lower()

    results = []
    for update in updates:
        # Check status filter if provided
        if status and update.status:
            if update.status.lower() != status.lower():
                continue
        elif status and not update.status:
            continue

        # Match query against title and description
        if query_lower in update.title.lower() or query_lower in update.description.lower():
            results.append(update.to_dict())

        if len(results) >= limit:
            break

    return results
