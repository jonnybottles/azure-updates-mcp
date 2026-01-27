"""Get update details tool for single update lookup."""

from ..feeds.azure_rss import fetch_updates


async def get_update_details(guid: str) -> dict | None:
    """Retrieve a specific Azure update by its GUID.

    Args:
        guid: The unique identifier of the update.

    Returns:
        The update object if found, or None if not found.
    """
    updates = await fetch_updates()

    for update in updates:
        if update.guid == guid:
            return update.to_dict()

    return None
