"""Unified search tool for querying and filtering Azure Updates."""

from datetime import datetime

import httpx
from fastmcp import Context

from ..feeds.azure_rss import fetch_updates
from ..models.input_models import SearchInput


async def azure_updates_search(ctx: Context, input: SearchInput) -> dict:
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
        input: SearchInput model with query, category, status, start_date, end_date, guid, and limit parameters

    Returns:
        Dictionary with:
        - total_found: Number of updates matching the filters (before applying limit)
        - updates: List of matching update objects (up to limit)
        - filters_applied: Summary of which filters were used
    """
    try:
        await ctx.info("Fetching Azure updates from RSS feed...")
        updates = await fetch_updates()
        await ctx.info(f"Retrieved {len(updates)} updates from feed")
    except httpx.HTTPError as e:
        await ctx.error(f"Failed to fetch updates: {str(e)}")
        return {
            "total_found": 0,
            "updates": [],
            "filters_applied": {"error": f"Failed to fetch Azure updates: {str(e)}"},
        }

    # GUID lookup is a fast path that ignores all other filters
    if input.guid:
        await ctx.info(f"Looking up update by GUID: {input.guid}")
        for update in updates:
            if update.guid == input.guid:
                return {
                    "total_found": 1,
                    "updates": [update.to_dict()],
                    "filters_applied": {"guid": input.guid},
                }
        return {
            "total_found": 0,
            "updates": [],
            "filters_applied": {"guid": input.guid},
        }

    # Limit is already validated by Pydantic (1-100)
    limit = input.limit

    # Parse date filters
    start_dt = None
    end_dt = None
    if input.start_date:
        try:
            start_dt = datetime.fromisoformat(input.start_date).replace(tzinfo=None)
        except ValueError:
            return {
                "total_found": 0,
                "updates": [],
                "filters_applied": {"error": f"Invalid start_date format: {input.start_date}"},
            }
    if input.end_date:
        try:
            end_dt = datetime.fromisoformat(input.end_date).replace(tzinfo=None)
        except ValueError:
            return {
                "total_found": 0,
                "updates": [],
                "filters_applied": {"error": f"Invalid end_date format: {input.end_date}"},
            }
    elif start_dt:
        # Default end_date to now when start_date is provided
        end_dt = datetime.now().replace(tzinfo=None)

    # Prepare lowercase values for case-insensitive matching
    query_lower = input.query.lower() if input.query else None
    category_lower = input.category.lower() if input.category else None
    status_lower = input.status.lower() if input.status else None

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
    if input.query:
        filters_applied["query"] = input.query
    if input.category:
        filters_applied["category"] = input.category
    if input.status:
        filters_applied["status"] = input.status
    if input.start_date:
        filters_applied["start_date"] = input.start_date
    if input.end_date or end_dt:
        filters_applied["end_date"] = input.end_date or end_dt.strftime("%Y-%m-%d")
    if not filters_applied:
        filters_applied["note"] = "No filters applied, returning most recent updates"

    return {
        "total_found": len(matched),
        "updates": [u.to_dict() for u in matched[:limit]],
        "filters_applied": filters_applied,
    }
