"""Tests for MCP tools."""

import pytest
from unittest.mock import AsyncMock

from azure_updates_mcp.tools.ping import ping
from azure_updates_mcp.models.input_models import SearchInput, SummarizeInput


# Mock Context for testing
class MockContext:
    """Mock FastMCP Context for testing."""

    async def info(self, message: str):
        """Mock info logging."""
        pass

    async def error(self, message: str):
        """Mock error logging."""
        pass

    async def report_progress(self, current: int, total: int, message: str = ""):
        """Mock progress reporting."""
        pass


# ---------------------------------------------------------------------------
# ping
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_ping_returns_status():
    """Test that ping returns expected structure."""
    result = await ping()

    assert result["status"] == "ok"
    assert result["service"] == "azure-updates-mcp"
    assert "timestamp" in result


# ---------------------------------------------------------------------------
# azure_updates_search
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_search_no_filters_returns_recent():
    """When called with no filters, returns the most recent updates."""
    from azure_updates_mcp.tools.search import azure_updates_search

    ctx = MockContext()
    input_data = SearchInput(limit=5)
    result = await azure_updates_search(ctx, input_data)

    assert isinstance(result, dict)
    assert "total_found" in result
    assert "updates" in result
    assert "filters_applied" in result
    assert len(result["updates"]) <= 5


@pytest.mark.asyncio
async def test_search_by_keyword():
    """Keyword filter matches title or description."""
    from azure_updates_mcp.tools.search import azure_updates_search

    ctx = MockContext()
    input_data = SearchInput(query="Azure", limit=5)
    result = await azure_updates_search(ctx, input_data)

    assert isinstance(result["updates"], list)
    for update in result["updates"]:
        text = (update["title"] + update["description"]).lower()
        assert "azure" in text
    assert result["filters_applied"].get("query") == "Azure"


@pytest.mark.asyncio
async def test_search_by_status():
    """Status filter returns only matching status."""
    from azure_updates_mcp.tools.search import azure_updates_search

    ctx = MockContext()
    input_data = SearchInput(status="Retirements", limit=5)
    result = await azure_updates_search(ctx, input_data)

    for update in result["updates"]:
        assert update["status"].lower() == "retirements"
    assert result["filters_applied"].get("status") == "Retirements"


@pytest.mark.asyncio
async def test_search_by_status_in_preview():
    """Status filter for 'In preview' returns preview features."""
    from azure_updates_mcp.tools.search import azure_updates_search

    ctx = MockContext()
    input_data = SearchInput(status="In preview", limit=5)
    result = await azure_updates_search(ctx, input_data)

    for update in result["updates"]:
        assert update["status"].lower() == "in preview"


@pytest.mark.asyncio
async def test_search_by_category():
    """Category filter with partial match returns matching updates."""
    from azure_updates_mcp.tools.search import azure_updates_search

    ctx = MockContext()
    input_data = SearchInput(category="Azure", limit=5)
    result = await azure_updates_search(ctx, input_data)

    assert isinstance(result["updates"], list)
    assert len(result["updates"]) <= 5
    assert result["filters_applied"].get("category") == "Azure"


@pytest.mark.asyncio
async def test_search_by_date_range():
    """Date range filter returns updates within the specified period."""
    from azure_updates_mcp.tools.search import azure_updates_search

    ctx = MockContext()
    input_data = SearchInput(start_date="2024-01-01", limit=5)
    result = await azure_updates_search(ctx, input_data)

    assert isinstance(result["updates"], list)
    assert len(result["updates"]) <= 5
    assert "start_date" in result["filters_applied"]


@pytest.mark.asyncio
async def test_search_invalid_date_returns_error():
    """Invalid date formats return an error in filters_applied."""
    from azure_updates_mcp.tools.search import azure_updates_search

    ctx = MockContext()
    input_data = SearchInput(start_date="not-a-date")
    result = await azure_updates_search(ctx, input_data)

    assert result["total_found"] == 0
    assert result["updates"] == []
    assert "error" in result["filters_applied"]


@pytest.mark.asyncio
async def test_search_by_guid():
    """GUID lookup retrieves a single specific update."""
    from azure_updates_mcp.tools.search import azure_updates_search

    ctx = MockContext()
    # First get a valid GUID
    input_data = SearchInput(limit=1)
    recent = await azure_updates_search(ctx, input_data)
    if recent["updates"]:
        guid = recent["updates"][0]["guid"]
        input_data = SearchInput(guid=guid)
        result = await azure_updates_search(ctx, input_data)

        assert result["total_found"] == 1
        assert result["updates"][0]["guid"] == guid
        assert result["filters_applied"].get("guid") == guid


@pytest.mark.asyncio
async def test_search_by_guid_not_found():
    """GUID lookup for nonexistent ID returns empty results."""
    from azure_updates_mcp.tools.search import azure_updates_search

    ctx = MockContext()
    input_data = SearchInput(guid="nonexistent-guid-12345")
    result = await azure_updates_search(ctx, input_data)

    assert result["total_found"] == 0
    assert result["updates"] == []


@pytest.mark.asyncio
async def test_search_combined_filters():
    """Multiple filters can be combined."""
    from azure_updates_mcp.tools.search import azure_updates_search

    ctx = MockContext()
    input_data = SearchInput(query="Azure", status="Launched", limit=5)
    result = await azure_updates_search(ctx, input_data)

    assert isinstance(result, dict)
    for update in result["updates"]:
        text = (update["title"] + update["description"]).lower()
        assert "azure" in text
        assert update["status"].lower() == "launched"


# ---------------------------------------------------------------------------
# azure_updates_summarize
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_summarize_all():
    """Summarize without time window returns overall stats."""
    from azure_updates_mcp.tools.summarize import azure_updates_summarize

    ctx = MockContext()
    input_data = SummarizeInput()
    result = await azure_updates_summarize(ctx, input_data)

    assert isinstance(result, dict)
    assert "total_updates" in result
    assert "by_status" in result
    assert "top_categories" in result
    assert "date_range" in result
    assert "highlights" in result

    # No period info when weeks is not specified
    if result["date_range"]:
        assert "period" not in result["date_range"]


@pytest.mark.asyncio
async def test_summarize_with_weeks():
    """Summarize with weeks parameter scopes to that time window."""
    from azure_updates_mcp.tools.summarize import azure_updates_summarize

    ctx = MockContext()
    input_data = SummarizeInput(weeks=2)
    result = await azure_updates_summarize(ctx, input_data)

    assert isinstance(result, dict)
    assert "total_updates" in result

    if result["date_range"]:
        assert "period" in result["date_range"]
        assert result["date_range"]["period"]["weeks"] == 2


@pytest.mark.asyncio
async def test_summarize_weeks_clamping():
    """Weeks parameter is validated by Pydantic (1-12)."""
    from azure_updates_mcp.tools.summarize import azure_updates_summarize

    ctx = MockContext()

    # Pydantic will reject weeks=0 (below minimum)
    with pytest.raises(Exception):
        input_data = SummarizeInput(weeks=0)

    # Pydantic will reject weeks=100 (above maximum)
    with pytest.raises(Exception):
        input_data = SummarizeInput(weeks=100)


@pytest.mark.asyncio
async def test_summarize_top_n():
    """top_n parameter controls how many categories and highlights appear."""
    from azure_updates_mcp.tools.summarize import azure_updates_summarize

    ctx = MockContext()
    input_data = SummarizeInput(top_n=3)
    result = await azure_updates_summarize(ctx, input_data)

    assert len(result["top_categories"]) <= 3
    assert len(result["highlights"]) <= 3


@pytest.mark.asyncio
async def test_summarize_category_structure():
    """Top categories include count and status breakdown."""
    from azure_updates_mcp.tools.summarize import azure_updates_summarize

    ctx = MockContext()
    input_data = SummarizeInput()
    result = await azure_updates_summarize(ctx, input_data)

    if result["top_categories"]:
        first = result["top_categories"][0]
        assert "category" in first
        assert "count" in first
        assert "statuses" in first


@pytest.mark.asyncio
async def test_summarize_highlight_structure():
    """Highlights include title, link, status, date, and categories."""
    from azure_updates_mcp.tools.summarize import azure_updates_summarize

    ctx = MockContext()
    input_data = SummarizeInput()
    result = await azure_updates_summarize(ctx, input_data)

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

    ctx = MockContext()
    result = await azure_updates_list_categories(ctx)

    assert isinstance(result, dict)
    assert "total_categories" in result
    assert "categories" in result
    assert isinstance(result["categories"], list)

    if result["categories"]:
        first = result["categories"][0]
        assert "name" in first
        assert "count" in first
