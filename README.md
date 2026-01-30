# Azure Updates MCP Server

A Python-based MCP (Model Context Protocol) server that provides tools for querying and searching the Azure Updates RSS feed.

## Features

- **ping** - Health check endpoint
- **list_updates** - List recent Azure service updates
- **search_updates** - Search updates by keyword with optional status filter

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

## Development

```bash
# Run tests
pytest

# Lint
ruff check src/ tests/
```

## License

MIT
