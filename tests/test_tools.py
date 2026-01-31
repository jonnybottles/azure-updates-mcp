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
# azure_updates_summarize
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_summarize_all():
    """Summarize without time window returns overall stats from facets."""
    from azure_updates_mcp.tools.summarize import azure_updates_summarize

    result = await azure_updates_summarize()

    assert isinstance(result, dict)
    assert "total_updates" in result
    assert "by_status" in result
    assert "top_categories" in result
    assert "date_range" in result
    assert "highlights" in result

    # Should have a large total from the full API
    assert result["total_updates"] > 100

    # No period info when weeks is not specified
    if result["date_range"]:
        assert "period" not in result["date_range"]


@pytest.mark.asyncio
async def test_summarize_with_weeks():
    """Summarize with weeks parameter scopes to that time window."""
    from azure_updates_mcp.tools.summarize import azure_updates_summarize

    result = await azure_updates_summarize(weeks=2)

    assert isinstance(result, dict)
    assert "total_updates" in result

    if result["date_range"]:
        assert "period" in result["date_range"]
        assert result["date_range"]["period"]["weeks"] == 2


@pytest.mark.asyncio
async def test_summarize_weeks_clamping():
    """Weeks parameter is clamped to 1-12."""
    from azure_updates_mcp.tools.summarize import azure_updates_summarize

    result_low = await azure_updates_summarize(weeks=0)
    if result_low["date_range"] and "period" in result_low["date_range"]:
        assert result_low["date_range"]["period"]["weeks"] == 1

    result_high = await azure_updates_summarize(weeks=100)
    if result_high["date_range"] and "period" in result_high["date_range"]:
        assert result_high["date_range"]["period"]["weeks"] == 12


@pytest.mark.asyncio
async def test_summarize_top_n():
    """top_n parameter controls how many categories and highlights appear."""
    from azure_updates_mcp.tools.summarize import azure_updates_summarize

    result = await azure_updates_summarize(top_n=3)

    assert len(result["top_categories"]) <= 3
    assert len(result["highlights"]) <= 3


@pytest.mark.asyncio
async def test_summarize_category_structure():
    """Top categories include count and status breakdown."""
    from azure_updates_mcp.tools.summarize import azure_updates_summarize

    result = await azure_updates_summarize()

    if result["top_categories"]:
        first = result["top_categories"][0]
        assert "category" in first
        assert "count" in first
        assert "statuses" in first


@pytest.mark.asyncio
async def test_summarize_highlight_structure():
    """Highlights include title, link, status, date, and categories."""
    from azure_updates_mcp.tools.summarize import azure_updates_summarize

    result = await azure_updates_summarize()

    if result["highlights"]:
        first = result["highlights"][0]
        assert "title" in first
        assert "link" in first
        assert "status" in first
        assert "date" in first
        assert "categories" in first


# ---------------------------------------------------------------------------
# azure_updates_list_categories
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_categories():
    """List categories returns category names with counts."""
    from azure_updates_mcp.tools.categories import azure_updates_list_categories

    result = await azure_updates_list_categories()

    assert isinstance(result, dict)
    assert "total_categories" in result
    assert "categories" in result
    assert isinstance(result["categories"], list)

    if result["categories"]:
        first = result["categories"][0]
        assert "name" in first
        assert "count" in first


@pytest.mark.asyncio
async def test_list_categories_has_taxonomy():
    """List categories returns structured taxonomy facets."""
    from azure_updates_mcp.tools.categories import azure_updates_list_categories

    result = await azure_updates_list_categories()

    assert "product_categories" in result
    assert "products" in result
    assert "tags" in result
    assert "statuses" in result

    # Should have real data from the API
    assert len(result["product_categories"]) > 0
    assert len(result["products"]) > 0
    assert len(result["statuses"]) > 0


@pytest.mark.asyncio
async def test_list_categories_total_count():
    """total_categories reflects the merged count of all taxonomy items."""
    from azure_updates_mcp.tools.categories import azure_updates_list_categories

    result = await azure_updates_list_categories()

    expected_total = (
        len(result["product_categories"])
        + len(result["products"])
        + len(result["tags"])
    )
    assert result["total_categories"] == expected_total
