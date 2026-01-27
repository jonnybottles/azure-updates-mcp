"""Tests for RSS feed functionality."""

import pytest

from azure_updates_mcp.feeds.azure_rss import fetch_updates


@pytest.mark.asyncio
async def test_fetch_updates_returns_list():
    """Test that fetch_updates returns a list of updates."""
    updates = await fetch_updates()

    assert isinstance(updates, list)
    assert len(updates) > 0


@pytest.mark.asyncio
async def test_update_has_required_fields():
    """Test that updates have all required fields."""
    updates = await fetch_updates()

    if updates:
        update = updates[0]
        assert update.guid
        assert update.title
        assert update.link
        assert update.pub_date is not None


@pytest.mark.asyncio
async def test_updates_sorted_by_date():
    """Test that updates are sorted newest first."""
    updates = await fetch_updates()

    if len(updates) >= 2:
        for i in range(len(updates) - 1):
            assert updates[i].pub_date >= updates[i + 1].pub_date
