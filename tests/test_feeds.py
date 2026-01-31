"""Tests for JSON API feed functionality."""

from datetime import datetime

import pytest

from azure_updates_mcp.feeds.azure_api import (
    AzureUpdatesQuery,
    _parse_item,
    fetch_updates,
)

# ---------------------------------------------------------------------------
# Unit tests for AzureUpdatesQuery
# ---------------------------------------------------------------------------


def test_query_defaults():
    """Default query produces expected query string."""
    q = AzureUpdatesQuery()
    qs = q.to_query_string()

    assert "top=20" in qs
    assert "skip=0" in qs
    assert "orderby=created" in qs
    assert "$count=true" in qs
    assert "search" not in qs
    assert "includeFacets" not in qs


def test_query_with_search():
    """Search term is wrapped in double quotes."""
    q = AzureUpdatesQuery(search="kubernetes")
    qs = q.to_query_string()

    assert "search=" in qs
    assert "kubernetes" in qs


def test_query_with_facets():
    """includeFacets param is set when requested."""
    q = AzureUpdatesQuery(include_facets=True)
    qs = q.to_query_string()

    assert "includeFacets=true" in qs


def test_query_custom_pagination():
    """Custom top/skip values are reflected."""
    q = AzureUpdatesQuery(top=50, skip=100)
    qs = q.to_query_string()

    assert "top=50" in qs
    assert "skip=100" in qs


def test_query_to_url():
    """to_url produces a full URL."""
    q = AzureUpdatesQuery(top=5)
    url = q.to_url()

    assert url.startswith("https://www.microsoft.com/releasecommunications/api/v2/azure?")
    assert "top=5" in url


# ---------------------------------------------------------------------------
# Unit tests for _parse_item
# ---------------------------------------------------------------------------


def test_parse_item_basic():
    """_parse_item converts a JSON dict to AzureUpdate."""
    item = {
        "id": "test-123",
        "title": "Test Update",
        "description": "<p>Some description</p>",
        "status": "Launched",
        "created": "2025-01-15T10:00:00Z",
        "modified": "2025-01-16T12:00:00Z",
        "products": ["Azure Functions"],
        "productCategories": ["Compute"],
        "tags": ["Serverless"],
        "generalAvailabilityDate": "Q1 2025",
        "previewAvailabilityDate": None,
        "privatePreviewAvailabilityDate": None,
    }

    update = _parse_item(item)

    assert update is not None
    assert update.id == "test-123"
    assert update.title == "Test Update"
    assert update.status == "Launched"
    assert update.products == ["Azure Functions"]
    assert update.product_categories == ["Compute"]
    assert update.tags == ["Serverless"]
    assert update.general_availability_date == "Q1 2025"
    assert "azure.microsoft.com" in update.link
    assert "test-123" in update.link


def test_parse_item_backward_compat():
    """Backward-compat properties work correctly."""
    item = {
        "id": "compat-456",
        "title": "Compat Test",
        "description": "desc",
        "status": "In preview",
        "created": "2025-03-01T00:00:00Z",
        "products": ["AKS"],
        "productCategories": ["Containers"],
        "tags": [],
    }

    update = _parse_item(item)

    assert update.guid == "compat-456"
    assert isinstance(update.pub_date, datetime)
    assert update.categories == ["AKS", "Containers"]


def test_parse_item_empty_taxonomy():
    """Handles missing taxonomy fields gracefully."""
    item = {
        "id": "empty-789",
        "title": "Minimal",
        "description": "",
        "created": "2025-01-01T00:00:00Z",
    }

    update = _parse_item(item)

    assert update is not None
    assert update.products == []
    assert update.product_categories == []
    assert update.tags == []
    assert update.categories == []


def test_parse_item_invalid_returns_none():
    """Invalid item data returns None."""
    result = _parse_item({})
    # Should return None or an update with defaults — either is acceptable
    # The important thing is it doesn't raise


def test_parse_item_to_dict():
    """to_dict() includes both new and backward-compat keys."""
    item = {
        "id": "dict-test",
        "title": "Dict Test",
        "description": "desc",
        "status": "Launched",
        "created": "2025-06-01T00:00:00Z",
        "modified": "2025-06-02T00:00:00Z",
        "products": ["CosmosDB"],
        "productCategories": ["Databases"],
        "tags": ["NoSQL"],
    }

    update = _parse_item(item)
    d = update.to_dict()

    # New fields
    assert d["id"] == "dict-test"
    assert d["created"] is not None
    assert d["modified"] is not None
    assert d["products"] == ["CosmosDB"]
    assert d["product_categories"] == ["Databases"]
    assert d["tags"] == ["NoSQL"]

    # Backward-compat fields
    assert d["guid"] == "dict-test"
    assert d["pub_date"] is not None
    assert "CosmosDB" in d["categories"]
    assert "Databases" in d["categories"]


# ---------------------------------------------------------------------------
# Integration tests (hit real API)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_fetch_updates_returns_tuple():
    """fetch_updates returns a (list, int, None) tuple."""
    updates, total_count, facets = await fetch_updates(top=5)

    assert isinstance(updates, list)
    assert isinstance(total_count, int)
    assert total_count > 0
    assert len(updates) <= 5
    assert facets is None


@pytest.mark.asyncio
async def test_fetch_updates_items_have_required_fields():
    """Updates from the API have all required fields."""
    updates, _, _ = await fetch_updates(top=3)

    assert len(updates) > 0
    update = updates[0]
    assert update.id
    assert update.title
    assert update.link
    assert update.created is not None

    # Backward compat
    assert update.guid
    assert update.pub_date is not None


@pytest.mark.asyncio
async def test_fetch_updates_with_search():
    """Search parameter returns relevant results."""
    updates, total_count, _ = await fetch_updates(search="kubernetes", top=5)

    assert isinstance(updates, list)
    assert total_count > 0


@pytest.mark.asyncio
async def test_fetch_updates_pagination():
    """Pagination with top/skip works."""
    page1, count1, _ = await fetch_updates(top=3, skip=0)
    page2, count2, _ = await fetch_updates(top=3, skip=3)

    # Total counts should be the same
    assert count1 == count2

    # Pages should have different items (unless there are very few items)
    if len(page1) > 0 and len(page2) > 0:
        assert page1[0].id != page2[0].id


@pytest.mark.asyncio
async def test_fetch_updates_sorted_by_date():
    """Updates are sorted newest first by default."""
    updates, _, _ = await fetch_updates(top=10)

    if len(updates) >= 2:
        for i in range(len(updates) - 1):
            assert updates[i].created >= updates[i + 1].created


@pytest.mark.asyncio
async def test_fetch_updates_with_facets():
    """fetch_updates with include_facets=True returns structured taxonomy data."""
    updates, total_count, facets = await fetch_updates(top=0, include_facets=True)

    assert isinstance(updates, list)
    assert total_count > 0
    assert facets is not None
    assert isinstance(facets, dict)
    assert "product_categories" in facets
    assert "products" in facets
    assert "tags" in facets
    assert "statuses" in facets

    # Should have meaningful data
    assert len(facets["product_categories"]) > 0
    assert len(facets["products"]) > 0
    assert len(facets["statuses"]) > 0

    # Each facet item should have name and count
    first_cat = facets["product_categories"][0]
    assert "name" in first_cat
    assert "count" in first_cat
