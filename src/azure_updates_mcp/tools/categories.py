"""Category discovery tool for listing available Azure service categories."""

from ..feeds.azure_api import fetch_facets


async def azure_updates_list_categories() -> dict:
    """List all available categories from Azure updates with occurrence counts.

    Returns a structured taxonomy of product categories, individual products,
    tags, and statuses with their occurrence counts. Uses the JSON API's
    faceted search for efficient aggregation.

    Use this to discover valid filter values before using
    azure_updates_search(product=...) or azure_updates_search(product_category=...).

    Returns:
        Dictionary with:
        - total_categories: Total unique count across all taxonomy types (backward compat)
        - categories: Flat list of {name, count} for all taxonomy items (backward compat)
        - product_categories: List of {name, count} for product category facets
        - products: List of {name, count} for product facets
        - tags: List of {name, count} for tag facets
        - statuses: List of {name, count} for status facets
    """
    facets = await fetch_facets()

    product_categories = facets.get("product_categories", [])
    products = facets.get("products", [])
    tags = facets.get("tags", [])
    statuses = facets.get("statuses", [])

    # Backward-compat: flat merged list sorted by count
    all_items = product_categories + products + tags
    all_items_sorted = sorted(all_items, key=lambda x: (-x["count"], x["name"]))

    return {
        "total_categories": len(all_items_sorted),
        "categories": all_items_sorted,
        "product_categories": product_categories,
        "products": products,
        "tags": tags,
        "statuses": statuses,
    }
