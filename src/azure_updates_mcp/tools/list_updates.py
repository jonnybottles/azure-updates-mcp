"""List updates tool for fetching Azure Updates."""

from ..feeds.azure_rss import fetch_updates


async def list_updates(limit: int = 10) -> list[dict]:
    """List recent Azure updates from the RSS feed.

    Args:
        limit: Maximum number of updates to return (default: 10, max: 100).

    Returns:
        List of update objects with title, description, date, status, and categories.
    """
    # Clamp limit to reasonable bounds
    limit = max(1, min(limit, 100))

    updates = await fetch_updates()
    return [update.to_dict() for update in updates[:limit]]
