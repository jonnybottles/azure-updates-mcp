"""Tests for MCP tools."""

import pytest

# ---------------------------------------------------------------------------
# azure_updates_search
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_search_no_filters_returns_recent():
    """When called with no filters, returns the most recent updates."""
    from azure_updates_mcp.tools.search import azure_updates_search

    result = await azure_updates_search(limit=5)

    assert isinstance(result, dict)
    assert "total_found" in result
    assert "updates" in result
    assert "filters_applied" in result
    assert len(result["updates"]) <= 5


@pytest.mark.asyncio
async def test_search_by_keyword():
    """Keyword filter uses server-side search."""
    from azure_updates_mcp.tools.search import azure_updates_search

    result = await azure_updates_search(query="Azure", limit=5)

    assert isinstance(result["updates"], list)
    assert result["filters_applied"].get("query") == "Azure"


@pytest.mark.asyncio
async def test_search_by_status():
    """Status filter returns only matching status."""
    from azure_updates_mcp.tools.search import azure_updates_search

    result = await azure_updates_search(status="Retirements", limit=5)

    for update in result["updates"]:
        assert update["status"].lower() == "retirements"
    assert result["filters_applied"].get("status") == "Retirements"


@pytest.mark.asyncio
async def test_search_by_status_in_preview():
    """Status filter for 'In preview' returns preview features."""
    from azure_updates_mcp.tools.search import azure_updates_search

    result = await azure_updates_search(status="In preview", limit=5)

    for update in result["updates"]:
        assert update["status"].lower() == "in preview"


@pytest.mark.asyncio
async def test_search_by_category():
    """Category filter with partial match returns matching updates."""
    from azure_updates_mcp.tools.search import azure_updates_search

    result = await azure_updates_search(category="Azure", limit=5)

    assert isinstance(result["updates"], list)
    assert len(result["updates"]) <= 5
    assert result["filters_applied"].get("category") == "Azure"


@pytest.mark.asyncio
async def test_search_by_date_range():
    """Date range filter returns updates within the specified period."""
    from azure_updates_mcp.tools.search import azure_updates_search

    result = await azure_updates_search(start_date="2024-01-01", limit=5)

    assert isinstance(result["updates"], list)
    assert len(result["updates"]) <= 5
    assert "start_date" in result["filters_applied"]


@pytest.mark.asyncio
async def test_search_invalid_date_returns_error():
    """Invalid date formats return an error in filters_applied."""
    from azure_updates_mcp.tools.search import azure_updates_search

    result = await azure_updates_search(start_date="not-a-date")

    assert result["total_found"] == 0
    assert result["updates"] == []
    assert "error" in result["filters_applied"]


@pytest.mark.asyncio
async def test_search_by_guid():
    """GUID lookup retrieves a single specific update."""
    from azure_updates_mcp.tools.search import azure_updates_search

    # First get a valid GUID
    recent = await azure_updates_search(limit=1)
    if recent["updates"]:
        guid = recent["updates"][0]["guid"]
        result = await azure_updates_search(guid=guid)

        assert result["total_found"] == 1
        assert result["updates"][0]["guid"] == guid
        assert result["filters_applied"].get("guid") == guid


@pytest.mark.asyncio
async def test_search_by_guid_not_found():
    """GUID lookup for nonexistent ID returns empty results."""
    from azure_updates_mcp.tools.search import azure_updates_search

    result = await azure_updates_search(guid="nonexistent-guid-12345")

    assert result["total_found"] == 0
    assert result["updates"] == []


@pytest.mark.asyncio
async def test_search_combined_filters():
    """Multiple filters can be combined."""
    from azure_updates_mcp.tools.search import azure_updates_search

    result = await azure_updates_search(
        query="Azure",
        status="Launched",
        limit=5,
    )

    assert isinstance(result, dict)
    for update in result["updates"]:
        assert update["status"].lower() == "launched"


@pytest.mark.asyncio
async def test_search_with_offset():
    """Offset parameter enables pagination."""
    from azure_updates_mcp.tools.search import azure_updates_search

    page1 = await azure_updates_search(limit=3, offset=0)
    page2 = await azure_updates_search(limit=3, offset=3)

    assert isinstance(page1["updates"], list)
    assert isinstance(page2["updates"], list)

    # Pages should have different items if enough results
    if page1["updates"] and page2["updates"]:
        assert page1["updates"][0]["id"] != page2["updates"][0]["id"]


@pytest.mark.asyncio
async def test_search_result_has_new_fields():
    """Search results include new JSON API fields."""
    from azure_updates_mcp.tools.search import azure_updates_search

    result = await azure_updates_search(limit=1)

    if result["updates"]:
        update = result["updates"][0]
        # New fields
        assert "id" in update
        assert "created" in update
        assert "products" in update
        assert "product_categories" in update
        assert "tags" in update
        # Backward-compat fields
        assert "guid" in update
        assert "pub_date" in update
        assert "categories" in update


@pytest.mark.asyncio
async def test_search_total_found_reflects_api_count():
    """total_found should reflect the API's total count, not just returned items."""
    from azure_updates_mcp.tools.search import azure_updates_search

    result = await azure_updates_search(limit=3)

    # total_found should be >= number of returned items
    assert result["total_found"] >= len(result["updates"])


# ---------------------------------------------------------------------------
# azure_updates_search with include_facets
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_search_without_facets_has_no_facets_key():
    """Default behavior: no facets key in response."""
    from azure_updates_mcp.tools.search import azure_updates_search

    result = await azure_updates_search(limit=3)

    assert isinstance(result, dict)
    assert "facets" not in result
    assert "total_found" in result
    assert "updates" in result


@pytest.mark.asyncio
async def test_search_with_facets_includes_taxonomy():
    """include_facets=True adds facets key with correct structure."""
    from azure_updates_mcp.tools.search import azure_updates_search

    result = await azure_updates_search(limit=3, include_facets=True)

    assert "facets" in result
    facets = result["facets"]
    assert "product_categories" in facets
    assert "products" in facets
    assert "tags" in facets
    assert "statuses" in facets

    # Should have real data
    assert len(facets["product_categories"]) > 0
    assert len(facets["products"]) > 0
    assert len(facets["statuses"]) > 0

    # Each facet item should have name and count
    first_cat = facets["product_categories"][0]
    assert "name" in first_cat
    assert "count" in first_cat

    # Should also return updates alongside facets
    assert len(result["updates"]) <= 3


@pytest.mark.asyncio
async def test_search_facets_only_with_limit_zero():
    """limit=0 with include_facets=True returns facets and empty updates."""
    from azure_updates_mcp.tools.search import azure_updates_search

    result = await azure_updates_search(limit=0, include_facets=True)

    assert result["updates"] == []
    assert "facets" in result
    assert result["total_found"] > 0
    assert len(result["facets"]["product_categories"]) > 0


@pytest.mark.asyncio
async def test_search_with_facets_and_filters():
    """Facets work alongside status/query filters."""
    from azure_updates_mcp.tools.search import azure_updates_search

    result = await azure_updates_search(
        status="Launched",
        include_facets=True,
        limit=3,
    )

    assert "facets" in result
    assert isinstance(result["facets"], dict)
    for update in result["updates"]:
        assert update["status"].lower() == "launched"
