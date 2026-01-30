# Azure Updates MCP Server

A Python-based MCP (Model Context Protocol) server that provides tools for querying and searching the Azure Updates RSS feed.

## Features

- **ping** - Health check endpoint
- **azure_updates_search** - Search and filter Azure updates by keyword, category, status, date range, or GUID
- **azure_updates_summarize** - Get statistical overview and trends of Azure updates
- **azure_updates_list_categories** - List all available Azure service categories

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

## Usage Examples

Once connected to Claude Desktop, you can ask questions like:

1. **Get recent updates**: "Show me the 10 most recent Azure updates"

2. **Search by keyword**: "Find all Azure updates related to Kubernetes or AKS"

3. **Filter by status**: "What Azure features are currently in preview?"

4. **Check for retirements**: "Are there any upcoming Azure service retirements I should know about?"

5. **Get overview**: "Give me a summary of Azure update activity over the last 2 weeks"

## Development

```bash
# Run tests
pytest

# Lint
ruff check src/ tests/
```

## License

MIT
