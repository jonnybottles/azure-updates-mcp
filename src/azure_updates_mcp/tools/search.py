"""Unified search tool for querying and filtering Azure Updates."""

from datetime import datetime

from ..feeds.azure_rss import fetch_updates


async def azure_updates_search(
    query: str | None = None,
    category: str | None = None,
    status: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    guid: str | None = None,
    limit: int = 10,
) -> dict:
    """Search, filter, and retrieve Azure service updates from the official RSS feed.

    Combines keyword search, category filtering, status filtering, and date range
    filtering into a single flexible tool. All filter parameters are optional and
    can be combined. When no filters are provided, returns the most recent updates.

    Use this tool to:
    - Browse recent updates (no filters)
    - Search for updates mentioning a specific topic (query="AKS")
    - Filter by service category (category="Azure Kubernetes Service")
    - Find updates by status (status="In preview", "Launched", "Retirements", "In development")
    - Get updates in a date range (start_date="2025-01-01", end_date="2025-01-31")
    - Retrieve a specific update by its GUID (guid="...")
    - Combine any of the above (query="networking" + status="Launched" + category="AKS")

    Args:
        query: Optional keyword to match against title and description (case-insensitive).
        category: Optional category to filter by (case-insensitive partial match,
            e.g. "AKS" matches "Azure Kubernetes Service (AKS)").
        status: Optional status filter. Valid values: Launched, In preview,
            In development, Retirements.
        start_date: Optional start date in ISO format (YYYY-MM-DD). Only include
            updates published on or after this date.
        end_date: Optional end date in ISO format (YYYY-MM-DD). Only include
            updates published on or before this date. Defaults to today when
            start_date is provided.
        guid: Optional unique identifier to retrieve a single specific update.
            When provided, all other filters are ignored and a single update is returned.
        limit: Maximum number of results to return (default: 10, max: 100).
            Ignored when guid is provided.

    Returns:
        Dictionary with:
        - total_found: Number of updates matching the filters (before applying limit)
        - updates: List of matching update objects (up to limit)
        - filters_applied: Summary of which filters were used
    """
    updates = await fetch_updates()

    # GUID lookup is a fast path that ignores all other filters
    if guid:
        for update in updates:
            if update.guid == guid:
                return {
                    "total_found": 1,
                    "updates": [update.to_dict()],
                    "filters_applied": {"guid": guid},
                }
        return {
            "total_found": 0,
            "updates": [],
            "filters_applied": {"guid": guid},
        }

    # Clamp limit to reasonable bounds
    limit = max(1, min(limit, 100))

    # Parse date filters
    start_dt = None
    end_dt = None
    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date).replace(tzinfo=None)
        except ValueError:
            return {
                "total_found": 0,
                "updates": [],
                "filters_applied": {"error": f"Invalid start_date format: {start_date}"},
            }
    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date).replace(tzinfo=None)
        except ValueError:
            return {
                "total_found": 0,
                "updates": [],
                "filters_applied": {"error": f"Invalid end_date format: {end_date}"},
            }
    elif start_dt:
        # Default end_date to now when start_date is provided
        end_dt = datetime.now().replace(tzinfo=None)

    # Prepare lowercase values for case-insensitive matching
    query_lower = query.lower() if query else None
    category_lower = category.lower() if category else None
    status_lower = status.lower() if status else None

    # Apply all filters
    matched = []
    for update in updates:
        # Status filter
        if status_lower:
            if not update.status or update.status.lower() != status_lower:
                continue

        # Category filter (partial match)
        if category_lower:
            if not any(category_lower in cat.lower() for cat in update.categories):
                continue

        # Date range filter
        if start_dt or end_dt:
            pub_dt = update.pub_date.replace(tzinfo=None)
            if start_dt and pub_dt < start_dt:
                continue
            if end_dt and pub_dt > end_dt:
                continue

        # Keyword search (title + description)
        if query_lower:
            if (
                query_lower not in update.title.lower()
                and query_lower not in update.description.lower()
            ):
                continue

        matched.append(update)

    # Build filters summary
    filters_applied: dict = {}
    if query:
        filters_applied["query"] = query
    if category:
        filters_applied["category"] = category
    if status:
        filters_applied["status"] = status
    if start_date:
        filters_applied["start_date"] = start_date
    if end_date or end_dt:
        filters_applied["end_date"] = end_date or end_dt.strftime("%Y-%m-%d")
    if not filters_applied:
        filters_applied["note"] = "No filters applied, returning most recent updates"

    return {
        "total_found": len(matched),
        "updates": [u.to_dict() for u in matched[:limit]],
        "filters_applied": filters_applied,
    }
