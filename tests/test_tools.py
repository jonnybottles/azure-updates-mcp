"""Tests for MCP tools."""

import pytest

from azure_updates_mcp.tools.ping import ping


def test_ping_returns_status():
    """Test that ping returns expected structure."""
    result = ping()

    assert result["status"] == "ok"
    assert result["service"] == "azure-updates-mcp"
    assert "timestamp" in result


@pytest.mark.asyncio
async def test_list_updates_limit():
    """Test that list_updates respects limit parameter."""
    from azure_updates_mcp.tools.list_updates import list_updates

    # This test requires network access
    results = await list_updates(limit=5)

    assert isinstance(results, list)
    assert len(results) <= 5

    if results:
        # Check structure of first result
        first = results[0]
        assert "title" in first
        assert "link" in first
        assert "pub_date" in first


@pytest.mark.asyncio
async def test_search_updates():
    """Test that search_updates filters by query."""
    from azure_updates_mcp.tools.search_updates import search_updates

    # Search for a common term
    results = await search_updates(query="Azure", limit=5)

    assert isinstance(results, list)
    # All results should contain "Azure" in title or description
    for result in results:
        text = (result["title"] + result["description"]).lower()
        assert "azure" in text


@pytest.mark.asyncio
async def test_list_categories():
    """Test that list_categories returns category structure."""
    from azure_updates_mcp.tools.list_categories import list_categories

    result = await list_categories()

    assert isinstance(result, dict)
    assert "total_categories" in result
    assert "categories" in result
    assert isinstance(result["categories"], list)

    if result["categories"]:
        first = result["categories"][0]
        assert "name" in first
        assert "count" in first


@pytest.mark.asyncio
async def test_get_updates_by_category():
    """Test that get_updates_by_category filters correctly."""
    from azure_updates_mcp.tools.get_updates_by_category import get_updates_by_category

    # Use "Azure" which should match many categories
    results = await get_updates_by_category(category="Azure", limit=5)

    assert isinstance(results, list)
    assert len(results) <= 5


@pytest.mark.asyncio
async def test_get_retirements():
    """Test that get_retirements returns retirement notices."""
    from azure_updates_mcp.tools.get_retirements import get_retirements

    results = await get_retirements(limit=5)

    assert isinstance(results, list)
    assert len(results) <= 5

    # All results should have Retirements status
    for result in results:
        assert result["status"].lower() == "retirements"


@pytest.mark.asyncio
async def test_get_previews():
    """Test that get_previews returns preview features."""
    from azure_updates_mcp.tools.get_previews import get_previews

    results = await get_previews(limit=5)

    assert isinstance(results, list)
    assert len(results) <= 5

    # All results should have "In preview" status
    for result in results:
        assert result["status"].lower() == "in preview"


@pytest.mark.asyncio
async def test_get_updates_summary():
    """Test that get_updates_summary returns aggregate statistics."""
    from azure_updates_mcp.tools.get_updates_summary import get_updates_summary

    result = await get_updates_summary()

    assert isinstance(result, dict)
    assert "total_updates" in result
    assert "by_status" in result
    assert "top_categories" in result
    assert "date_range" in result


@pytest.mark.asyncio
async def test_get_updates_by_date_range():
    """Test that get_updates_by_date_range filters by date."""
    from azure_updates_mcp.tools.get_updates_by_date_range import get_updates_by_date_range

    # Use a wide date range that should include results
    results = await get_updates_by_date_range(
        start_date="2024-01-01",
        limit=5,
    )

    assert isinstance(results, list)
    assert len(results) <= 5


@pytest.mark.asyncio
async def test_get_updates_by_date_range_invalid_date():
    """Test that get_updates_by_date_range handles invalid dates."""
    from azure_updates_mcp.tools.get_updates_by_date_range import get_updates_by_date_range

    results = await get_updates_by_date_range(start_date="not-a-date")

    assert results == []


@pytest.mark.asyncio
async def test_get_update_details():
    """Test that get_update_details retrieves a single update."""
    from azure_updates_mcp.tools.get_update_details import get_update_details
    from azure_updates_mcp.tools.list_updates import list_updates

    # First get a valid GUID from list_updates
    updates = await list_updates(limit=1)

    if updates:
        guid = updates[0]["guid"]
        result = await get_update_details(guid=guid)

        assert result is not None
        assert result["guid"] == guid


@pytest.mark.asyncio
async def test_get_update_details_not_found():
    """Test that get_update_details returns None for invalid GUID."""
    from azure_updates_mcp.tools.get_update_details import get_update_details

    result = await get_update_details(guid="nonexistent-guid-12345")

    assert result is None


@pytest.mark.asyncio
async def test_get_two_week_summary_structure():
    """Test that get_two_week_summary returns expected structure."""
    from azure_updates_mcp.tools.two_week_summary import get_two_week_summary

    result = await get_two_week_summary()

    assert isinstance(result, dict)
    assert "period" in result
    assert "total_count" in result
    assert "by_status" in result
    assert "by_category" in result
    assert "highlights" in result

    # Check period structure
    period = result["period"]
    assert "start" in period
    assert "end" in period
    assert "weeks" in period
    assert period["weeks"] == 2  # Default value

    # Check by_category structure if there are results
    if result["by_category"]:
        first_category = result["by_category"][0]
        assert "category" in first_category
        assert "count" in first_category
        assert "statuses" in first_category

    # Check highlights structure if there are results
    if result["highlights"]:
        first_highlight = result["highlights"][0]
        assert "title" in first_highlight
        assert "link" in first_highlight
        assert "status" in first_highlight
        assert "date" in first_highlight
        assert "categories" in first_highlight


@pytest.mark.asyncio
async def test_get_two_week_summary_custom_weeks():
    """Test that get_two_week_summary respects weeks parameter."""
    from azure_updates_mcp.tools.two_week_summary import get_two_week_summary

    result = await get_two_week_summary(weeks=4)

    assert result["period"]["weeks"] == 4


@pytest.mark.asyncio
async def test_get_two_week_summary_parameter_clamping():
    """Test that get_two_week_summary clamps parameters to valid ranges."""
    from azure_updates_mcp.tools.two_week_summary import get_two_week_summary

    # Test weeks clamping (should be clamped to 1-12)
    result_low = await get_two_week_summary(weeks=0)
    assert result_low["period"]["weeks"] == 1

    result_high = await get_two_week_summary(weeks=100)
    assert result_high["period"]["weeks"] == 12


@pytest.mark.asyncio
async def test_get_two_week_summary_highlights_limit():
    """Test that get_two_week_summary respects highlight_count parameter."""
    from azure_updates_mcp.tools.two_week_summary import get_two_week_summary

    result = await get_two_week_summary(highlight_count=3)

    # Should have at most 3 highlights
    assert len(result["highlights"]) <= 3
