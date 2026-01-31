"""Unified search tool for querying and filtering Azure Updates."""

from datetime import datetime

from ..feeds.azure_api import fetch_updates


async def azure_updates_search(
    query: str | None = None,
    category: str | None = None,
    status: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    guid: str | None = None,
    limit: int = 10,
    offset: int = 0,
    product: str | None = None,
    product_category: str | None = None,
    include_facets: bool = False,
) -> dict:
    """Search, filter, and retrieve Azure service updates from the official JSON API.

    Combines keyword search, category filtering, status filtering, and date range
    filtering into a single flexible tool. All filter parameters are optional and
    can be combined. When no filters are provided, returns the most recent updates.

    Use this tool to:
    - Browse recent updates (no filters)
    - Search for updates mentioning a specific topic (query="AKS")
    - Filter by product (product="Azure Kubernetes Service")
    - Filter by product category (product_category="Compute")
    - Filter by service category (category="Azure Kubernetes Service") -- partial match across all taxonomy
    - Find updates by status (status="In preview", "Launched", "Retirements", "In development")
    - Get updates in a date range (start_date="2025-01-01", end_date="2025-01-31")
    - Retrieve a specific update by its GUID/ID (guid="...")
    - Combine any of the above (query="networking" + status="Launched")
    - Paginate with offset (offset=10, limit=10 for page 2)
    - Discover available categories and taxonomy (include_facets=True, limit=0)
    - Get an overview with facets + recent items (include_facets=True, limit=10)

    Args:
        query: Optional keyword for server-side full-text search.
        category: Optional category to filter by (case-insensitive partial match
            across products, product_categories, and tags).
        status: Optional status filter. Valid values: Launched, In preview,
            In development, Retirements.
        start_date: Optional start date in ISO format (YYYY-MM-DD). Only include
            updates created on or after this date.
        end_date: Optional end date in ISO format (YYYY-MM-DD). Only include
            updates created on or before this date. Defaults to today when
            start_date is provided.
        guid: Optional unique identifier to retrieve a single specific update.
            When provided, all other filters are ignored and a single update is returned.
        limit: Maximum number of results to return (default: 10, max: 100).
            Set to 0 with include_facets=True for a facets-only response.
            Ignored when guid is provided.
        offset: Number of results to skip for pagination (default: 0).
        product: Optional product name filter (exact match against products list).
        product_category: Optional product category filter (exact match).
        include_facets: When True, includes taxonomy facets (product_categories,
            products, tags, statuses) with occurrence counts in the response.
            Use with limit=0 to get only facets (replaces category listing).

    Returns:
        Dictionary with:
        - total_found: Number of updates matching the filters (from API count)
        - updates: List of matching update objects (up to limit)
        - filters_applied: Summary of which filters were used
        - facets: (only when include_facets=True) Taxonomy with product_categories,
            products, tags, and statuses lists, each containing {name, count} items
    """
    # GUID lookup is a fast path that ignores all other filters
    if guid:
        # Fetch with search for the specific ID
        updates, _, _ = await fetch_updates(search=guid, top=20)
        for update in updates:
            if update.id == guid:
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
    limit = max(0, min(limit, 100))
    offset = max(0, offset)

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

    # Determine if we need client-side filtering
    needs_client_filter = any([
        category,
        product,
        product_category,
        start_dt,
        end_dt,
    ])

    # When client-side filtering is needed, fetch more items to filter from
    api_top = max(limit * 5, 1) if needs_client_filter else limit
    api_skip = 0 if needs_client_filter else offset

    updates, total_count, facets = await fetch_updates(
        search=query,
        status=status,
        top=api_top,
        skip=api_skip,
        order_by="created desc",
        include_facets=include_facets,
    )

    # Apply client-side filters
    if needs_client_filter:
        category_lower = category.lower() if category else None
        product_lower = product.lower() if product else None
        product_category_lower = product_category.lower() if product_category else None

        matched = []
        for update in updates:
            # Category filter (partial match across all taxonomy)
            if category_lower:
                all_cats = update.categories
                if not any(category_lower in cat.lower() for cat in all_cats):
                    continue

            # Product filter (exact match)
            if product_lower:
                if not any(product_lower == p.lower() for p in update.products):
                    continue

            # Product category filter (exact match)
            if product_category_lower:
                if not any(product_category_lower == pc.lower() for pc in update.product_categories):
                    continue

            # Date range filter
            if start_dt or end_dt:
                created_dt = update.created.replace(tzinfo=None)
                if start_dt and created_dt < start_dt:
                    continue
                if end_dt and created_dt > end_dt:
                    continue

            matched.append(update)

        # Apply offset and limit to client-filtered results
        total_found = len(matched)
        result_updates = matched[offset : offset + limit]
    else:
        total_found = total_count
        result_updates = updates

    # Build filters summary
    filters_applied: dict = {}
    if query:
        filters_applied["query"] = query
    if category:
        filters_applied["category"] = category
    if product:
        filters_applied["product"] = product
    if product_category:
        filters_applied["product_category"] = product_category
    if status:
        filters_applied["status"] = status
    if start_date:
        filters_applied["start_date"] = start_date
    if end_date or end_dt:
        filters_applied["end_date"] = end_date or end_dt.strftime("%Y-%m-%d")
    if offset > 0:
        filters_applied["offset"] = offset
    if not filters_applied:
        filters_applied["note"] = "No filters applied, returning most recent updates"

    response = {
        "total_found": total_found,
        "updates": [u.to_dict() for u in result_updates],
        "filters_applied": filters_applied,
    }
    if facets is not None:
        response["facets"] = facets
    return response
