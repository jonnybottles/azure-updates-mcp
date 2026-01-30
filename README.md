# Azure Updates MCP Server

A Python-based MCP (Model Context Protocol) server that provides tools for querying and searching the Azure Updates RSS feed.

## Available Tools

- **ping** - Health check endpoint that returns service status
- **azure_updates_search** - Search and filter Azure updates with multiple options:
  - Keyword search across titles and descriptions
  - Filter by category (e.g., "Azure Kubernetes Service")
  - Filter by status (Launched, In preview, In development, Retirements)
  - Date range filtering (start_date, end_date)
  - GUID lookup for specific updates
  - Combine multiple filters
  - Control result limit (default: 10, max: 100)
- **azure_updates_summarize** - Get aggregate statistics and dashboard-style overview:
  - Count updates by status
  - Top categories with status breakdowns
  - Recent highlights
  - Optional time window (last N weeks)
- **azure_updates_list_categories** - Discover available Azure service categories with occurrence counts

## Installation

```bash
pip install -e .
```

For development:

```bash
pip install -e ".[dev]"
```

## Usage

### Run the MCP Server

The server uses stdio transport by default, which is the recommended way to use MCP servers with Claude Desktop and other MCP clients:

```bash
python -m azure_updates_mcp.server
```

### Connect from Claude Desktop

Add to your Claude Desktop MCP config (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "azure-updates": {
      "command": "python",
      "args": ["-m", "azure_updates_mcp.server"],
      "cwd": "/path/to/azure-updates-mcp"
    }
  }
}
```

Or if using uv:

```json
{
  "mcpServers": {
    "azure-updates": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/azure-updates-mcp", "azure-updates-mcp"]
    }
  }
}
```

On Windows (`%APPDATA%\Claude\claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "azure-updates": {
      "command": "python",
      "args": ["-m", "azure_updates_mcp.server"],
      "cwd": "C:\\Users\\YourUsername\\path\\to\\azure-updates-mcp"
    }
  }
}
```

## Usage Examples

Once connected to Claude Desktop, you can use these tools in your conversations:

**Search for Recent Updates**
```
Show me the 10 most recent Azure updates
```

**Search by Keyword and Status**
```
Find all launched Kubernetes features in Azure
```

**Filter by Category and Date Range**
```
What compute updates were released in January 2025?
```

**Get Summary Statistics**
```
Give me a summary of Azure updates from the last 4 weeks
```

**Discover Categories**
```
What Azure service categories are available?
```

The MCP server will automatically use the appropriate tool (azure_updates_search, azure_updates_summarize, or azure_updates_list_categories) based on your query.

## Development

```bash
# Run tests
pytest

# Lint
ruff check src/ tests/
```

## License

MIT
