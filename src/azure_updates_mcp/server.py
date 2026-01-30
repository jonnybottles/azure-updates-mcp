"""Azure Updates MCP Server - FastMCP server with stdio/HTTP transport."""

from fastmcp import FastMCP

from .config import Config
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
    if Config.MCP_TRANSPORT == "http":
        print(f"Starting Azure Updates MCP server on {Config.MCP_HOST}:{Config.MCP_PORT}")
        print(f"MCP endpoint: http://{Config.MCP_HOST}:{Config.MCP_PORT}/mcp")
        mcp.run(transport="http", host=Config.MCP_HOST, port=Config.MCP_PORT)
    else:
        # stdio transport (default for MCP client auto-start)
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
