"""Azure Updates MCP Server - FastMCP server with stdio/HTTP transport."""

import os

from fastmcp import FastMCP

from .tools.categories import azure_updates_list_categories
from .tools.ping import ping
from .tools.search import azure_updates_search
from .tools.summarize import azure_updates_summarize

# Create the MCP server
mcp = FastMCP(
    "Azure Updates MCP",
    instructions=(
        "Query and search Azure service updates from the official RSS feed. "
        "Use azure_updates_search to find, filter, and retrieve updates. "
        "Use azure_updates_summarize for aggregate statistics and overviews. "
        "Use azure_updates_list_categories to discover available category values."
    ),
)

# Register tools
mcp.tool(ping)
mcp.tool(azure_updates_search)
mcp.tool(azure_updates_summarize)
mcp.tool(azure_updates_list_categories)


def main():
    """Run the MCP server.

    Uses stdio transport by default (for MCP client auto-start).
    Set MCP_TRANSPORT=http to run as an HTTP server for remote access.
    """
    transport = os.getenv("MCP_TRANSPORT", "stdio")

    if transport == "http":
        host = os.getenv("MCP_HOST", "0.0.0.0")
        port = int(os.getenv("MCP_PORT", "8000"))
        print(f"Starting Azure Updates MCP server on {host}:{port}")
        print(f"MCP endpoint: http://{host}:{port}/mcp")
        mcp.run(transport="http", host=host, port=port)
    else:
        # stdio transport (default for MCP client auto-start)
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
