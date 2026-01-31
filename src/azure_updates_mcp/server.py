"""Azure Updates MCP Server - FastMCP server with stdio/HTTP transport."""

import logging
import os

from fastmcp import FastMCP

# Suppress FastMCP's INFO logs to reduce console noise
logging.getLogger("fastmcp").setLevel(logging.WARNING)

from .tools.search import azure_updates_search

# Create the MCP server
mcp = FastMCP(
    "Azure Updates MCP",
    instructions=(
        "Query and search Azure service updates from the official JSON API. "
        "Use azure_updates_search to find, filter, and retrieve updates. "
        "Set include_facets=True to get taxonomy counts (product categories, "
        "products, tags, statuses). Use limit=0 with include_facets=True for "
        "a facets-only response to discover available filter values."
    ),
)

# Register tools
mcp.tool(azure_updates_search)


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
        mcp.run(transport="http", host=host, port=port, show_banner=False)
    else:
        # stdio transport (default for MCP client auto-start)
        mcp.run(transport="stdio", show_banner=False)


if __name__ == "__main__":
    main()
