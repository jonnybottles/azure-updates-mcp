"""Azure Updates JSON API client for fetching and parsing updates."""

from datetime import datetime
from urllib.parse import urlencode

import httpx

from ..models.update import AzureUpdate

AZURE_UPDATES_API_URL = "https://www.microsoft.com/releasecommunications/api/v2/azure"


class AzureUpdatesQuery:
    """Builds OData-style query parameters for the Azure Updates API."""

    def __init__(
        self,
        search: str | None = None,
        top: int = 20,
        skip: int = 0,
        order_by: str = "created desc",
        count: bool = True,
        include_facets: bool = False,
    ):
        self.search = search
        self.top = top
        self.skip = skip
        self.order_by = order_by
        self.count = count
        self.include_facets = include_facets

    def to_query_string(self) -> str:
        """Build a raw query string preserving literal $ in param names."""
        parts: list[str] = []

        if self.search:
            parts.append(urlencode({"search": f'"{self.search}"'}))
        parts.append(urlencode({"top": str(self.top)}))
        parts.append(urlencode({"skip": str(self.skip)}))
        parts.append(urlencode({"orderby": self.order_by}))
        if self.count:
            # $count must stay literal — urlencode would escape the $
            parts.append("$count=true")
        if self.include_facets:
            parts.append(urlencode({"includeFacets": "true"}))

        return "&".join(parts)

    def to_url(self) -> str:
        """Build the full request URL."""
        return f"{AZURE_UPDATES_API_URL}?{self.to_query_string()}"


async def fetch_updates(
    search: str | None = None,
    status: str | None = None,
    top: int = 20,
    skip: int = 0,
    order_by: str = "created desc",
) -> tuple[list[AzureUpdate], int]:
    """Fetch and parse Azure Updates from the JSON API.

    Args:
        search: Optional search term for server-side full-text search.
        status: Optional status filter (applied client-side from results).
        top: Maximum number of results to return from the API.
        skip: Number of results to skip (for pagination).
        order_by: Sort order (default: "created desc").

    Returns:
        Tuple of (list of AzureUpdate objects, total count from API).
    """
    query = AzureUpdatesQuery(
        search=search,
        top=top,
        skip=skip,
        order_by=order_by,
        count=True,
        include_facets=False,
    )

    async with httpx.AsyncClient() as client:
        response = await client.get(query.to_url(), timeout=30.0)
        response.raise_for_status()

    data = response.json()
    total_count = data.get("@odata.count", 0)
    items = data.get("value", [])

    updates = []
    for item in items:
        update = _parse_item(item)
        if update:
            # Client-side status filter if specified
            if status and (not update.status or update.status.lower() != status.lower()):
                continue
            updates.append(update)

    return updates, total_count


async def fetch_facets() -> dict:
    """Fetch faceted counts without item data.

    Returns:
        Dictionary with facet data: product_categories, products, tags, statuses.
    """
    query = AzureUpdatesQuery(
        top=0,
        skip=0,
        count=True,
        include_facets=True,
    )

    async with httpx.AsyncClient() as client:
        response = await client.get(query.to_url(), timeout=30.0)
        response.raise_for_status()

    data = response.json()
    total_count = data.get("@odata.count", 0)
    facets_list = data.get("facets", [])

    # Convert facets list into a dict keyed by facet name
    facets_by_name: dict[str, list[dict]] = {}
    for facet in facets_list:
        name = facet.get("name", "")
        values = facet.get("values", [])
        facets_by_name[name] = values

    def extract_facet(name: str) -> list[dict]:
        """Extract a facet's values into [{name, count}] format."""
        items = facets_by_name.get(name, [])
        result = []
        for item in items:
            value = item.get("value")
            count = item.get("count", 0)
            if value:
                result.append({"name": value, "count": count})
        return sorted(result, key=lambda x: (-x["count"], x["name"]))

    return {
        "total_count": total_count,
        "product_categories": extract_facet("ProductCategory"),
        "products": extract_facet("Product"),
        "tags": extract_facet("Tags"),
        "statuses": extract_facet("Status"),
    }


def _parse_item(item: dict) -> AzureUpdate | None:
    """Parse a single JSON API item into an AzureUpdate.

    Args:
        item: A dictionary from the API response's 'value' array.

    Returns:
        AzureUpdate object or None if parsing fails.
    """
    try:
        item_id = str(item.get("id", ""))
        title = item.get("title", "")
        description = item.get("description", "")
        status = item.get("status", None)

        # Parse dates
        created = _parse_api_date(item.get("created")) or datetime.now()
        modified = _parse_api_date(item.get("modified"))

        # Construct link
        link = f"https://azure.microsoft.com/en-us/updates?id={item_id}" if item_id else ""

        # Taxonomy fields are flat string lists in the API response
        products = [p for p in item.get("products", []) if isinstance(p, str)]
        product_categories = [
            p for p in item.get("productCategories", []) if isinstance(p, str)
        ]
        tags = [t for t in item.get("tags", []) if isinstance(t, str)]

        # Additional date strings
        ga_date = item.get("generalAvailabilityDate")
        preview_date = item.get("previewAvailabilityDate")
        private_preview_date = item.get("privatePreviewAvailabilityDate")

        return AzureUpdate(
            id=item_id,
            title=title,
            link=link,
            description=description,
            status=status,
            created=created,
            modified=modified,
            products=products,
            product_categories=product_categories,
            tags=tags,
            general_availability_date=ga_date,
            preview_availability_date=preview_date,
            private_preview_availability_date=private_preview_date,
        )
    except Exception:
        return None


def _parse_api_date(date_str: str | None) -> datetime | None:
    """Parse an ISO date string from the API.

    Args:
        date_str: ISO format date string or None.

    Returns:
        datetime object or None if parsing fails.
    """
    if not date_str:
        return None
    try:
        # Handle ISO format with or without timezone
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return dt.replace(tzinfo=None)
    except (ValueError, TypeError):
        return None
