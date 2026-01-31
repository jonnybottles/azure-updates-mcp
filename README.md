# Azure Updates MCP Server

A Python-based MCP (Model Context Protocol) server that provides tools for querying and searching the Azure Updates RSS feed.

## Quick Install

[![Install in VS Code](https://img.shields.io/badge/Install_in-VS_Code-0078d4?style=flat-square&logo=visualstudiocode)](https://vscode.dev/redirect/mcp/install?name=azure-updates-mcp&config=%7B%22type%22%3A%20%22stdio%22%2C%20%22command%22%3A%20%22uv%22%2C%20%22args%22%3A%20%5B%22run%22%2C%20%22azure-updates-mcp%22%5D%7D)
[![Install in Cursor](https://img.shields.io/badge/Install_in-Cursor-000000?style=flat-square&logo=cursor)](https://vscode.dev/redirect/mcp/install?name=azure-updates-mcp&config=%7B%22type%22%3A%20%22stdio%22%2C%20%22command%22%3A%20%22uv%22%2C%20%22args%22%3A%20%5B%22run%22%2C%20%22azure-updates-mcp%22%5D%7D)
[![Install in Claude Code](https://img.shields.io/badge/Install_in-Claude_Code-9b6bff?style=flat-square&logo=anthropic)](https://code.claude.com/docs/en/mcp)
[![Install in Copilot CLI](https://img.shields.io/badge/Install_in-Copilot_CLI-28a745?style=flat-square&logo=github)](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/use-copilot-cli)

> **One-click install:** Click VS Code or Cursor badges for automatic setup (requires [uv](https://github.com/astral-sh/uv) installed)
> **Manual install:** See instructions below for Claude Code, Copilot CLI, or Claude Desktop

## Features

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

Add to your Claude Desktop MCP config:
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

**Option 1: Using uv (recommended)**

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

**Option 2: Using Python directly**

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

### Connect from Claude Code

**Option 1: Using uv (recommended)**

```bash
claude mcp add --transport stdio azure-updates -- uv run azure-updates-mcp
```

**Option 2: Using Python directly**

```bash
claude mcp add --transport stdio azure-updates -- python -m azure_updates_mcp.server
```

Verify the server was added:

```bash
claude mcp list
```

### Connect from GitHub Copilot CLI

Add to your Copilot CLI MCP config (`~/.copilot/mcp-config.json`):

**Option 1: Using uv (recommended)**

```json
{
  "mcpServers": {
    "azure-updates": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "azure-updates-mcp"]
    }
  }
}
```

**Option 2: Using Python directly**

```json
{
  "mcpServers": {
    "azure-updates": {
      "type": "stdio",
      "command": "python",
      "args": ["-m", "azure_updates_mcp.server"],
      "cwd": "/path/to/azure-updates-mcp"
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
