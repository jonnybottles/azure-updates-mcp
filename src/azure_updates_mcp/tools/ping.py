"""Ping tool for health checks and debugging."""

from datetime import datetime, timezone


async def ping() -> dict:
    """Health check endpoint for the Azure Updates MCP server.

    Returns:
        Dictionary with status and server timestamp.
    """
    return {
        "status": "ok",
        "service": "azure-updates-mcp",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
