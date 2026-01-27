"""Azure Updates MCP Server - FastMCP server with HTTP transport."""

import os

from fastmcp import FastMCP

from .tools.get_previews import get_previews
from .tools.get_retirements import get_retirements
from .tools.get_update_details import get_update_details
from .tools.get_updates_by_category import get_updates_by_category
from .tools.get_updates_by_date_range import get_updates_by_date_range
from .tools.get_updates_summary import get_updates_summary
from .tools.list_categories import list_categories
from .tools.list_updates import list_updates
from .tools.ping import ping
from .tools.search_updates import search_updates
from .tools.two_week_summary import get_two_week_summary

# Create the MCP server
mcp = FastMCP(
    "Azure Updates MCP",
    instructions="Query and search Azure service updates from the official RSS feed",
)

# Register tools
mcp.tool(ping)
mcp.tool(list_updates)
mcp.tool(search_updates)
mcp.tool(list_categories)
mcp.tool(get_updates_by_category)
mcp.tool(get_retirements)
mcp.tool(get_previews)
mcp.tool(get_updates_summary)
mcp.tool(get_updates_by_date_range)
mcp.tool(get_update_details)
mcp.tool(get_two_week_summary)


def main():
    """Run the MCP server with HTTP transport."""
    host = os.getenv("MCP_HOST", "0.0.0.0")
    port = int(os.getenv("MCP_PORT", "8000"))

    print(f"Starting Azure Updates MCP server on {host}:{port}")
    print(f"MCP endpoint: http://{host}:{port}/mcp")

    mcp.run(transport="http", host=host, port=port)


if __name__ == "__main__":
    main()
