"""Get updates by date range tool for time-based filtering."""

from datetime import datetime

from ..feeds.azure_rss import fetch_updates


async def get_updates_by_date_range(
    start_date: str,
    end_date: str | None = None,
    limit: int = 50,
    status: str | None = None,
) -> list[dict]:
    """Filter Azure updates by publication date range.

    Args:
        start_date: Start date in ISO format (YYYY-MM-DD). Includes updates from this date.
        end_date: Optional end date in ISO format (YYYY-MM-DD). Defaults to today.
        limit: Maximum number of results to return (default: 50, max: 100).
        status: Optional status filter (Launched, In preview, In development, Retirements).

    Returns:
        List of matching update objects sorted by publication date.
    """
    # Clamp limit to reasonable bounds
    limit = max(1, min(limit, 100))

    # Parse dates
    try:
        start_dt = datetime.fromisoformat(start_date)
    except ValueError:
        return []  # Invalid start date

    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date)
        except ValueError:
            return []  # Invalid end date
    else:
        end_dt = datetime.now()

    # Make dates timezone-naive for comparison
    start_dt = start_dt.replace(tzinfo=None)
    end_dt = end_dt.replace(tzinfo=None)

    updates = await fetch_updates()

    results = []
    for update in updates:
        # Make comparison date timezone-naive
        pub_dt = update.pub_date.replace(tzinfo=None)

        # Check date range (inclusive)
        if not (start_dt <= pub_dt <= end_dt):
            continue

        # Check status filter if provided
        if status and update.status:
            if update.status.lower() != status.lower():
                continue
        elif status and not update.status:
            continue

        results.append(update.to_dict())

        if len(results) >= limit:
            break

    return results
