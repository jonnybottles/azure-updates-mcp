# Azure Updates MCP Server

mcp-name: io.github.jonnybottles/azure-updates

A Python-based MCP (Model Context Protocol) server that provides tools for querying and searching [Azure Updates](https://azure.microsoft.com/en-us/updates/).

## Requirements

### General

- **Python 3.9+**
- An MCP-compatible client (Claude Desktop, Cursor, Claude Code, GitHub Copilot CLI, etc.)

### Using `uvx` (Recommended)

If you are installing or running the server via **`uvx`**, you must have **uv** installed first.

- **uv** (includes `uvx`): https://github.com/astral-sh/uv

Install uv:

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
irm https://astral.sh/uv/install.ps1 | iex
```

Verify installation:

```bash
uv --version
uvx --version
```

> `uvx` allows you to run the MCP server without installing the package globally.

### Using pip (Alternative)

If you prefer not to use `uvx`, you can install the package directly with pip.

```bash
pip install azure-updates-mcp
```

In this case, `uv` / `uvx` is **not required**.

## Installation

### Install from PyPI

```bash
uvx azure-updates-mcp
```

Or install with pip:

```bash
pip install azure-updates-mcp
```

### Upgrade to Latest Version

```bash
uvx azure-updates-mcp@latest
```

Or with pip:

```bash
pip install --upgrade azure-updates-mcp
```


## Quick Setup

[![Set up in VS Code](https://img.shields.io/badge/Set_up_in-VS_Code-0078d4?style=flat-square&logo=visualstudiocode)](https://vscode.dev/redirect/mcp/install?name=azure-updates-mcp&config=%7B%22type%22%3A%20%22stdio%22%2C%20%22command%22%3A%20%22uvx%22%2C%20%22args%22%3A%20%5B%22azure-updates-mcp%22%5D%7D)
[![Set up in Cursor](https://img.shields.io/badge/Set_up_in-Cursor-000000?style=flat-square&logo=cursor)](https://cursor.com/docs/context/mcp)
[![Set up in Claude Code](https://img.shields.io/badge/Set_up_in-Claude_Code-9b6bff?style=flat-square&logo=anthropic)](https://code.claude.com/docs/en/mcp)
[![Set up in Copilot CLI](https://img.shields.io/badge/Set_up_in-Copilot_CLI-28a745?style=flat-square&logo=github)](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/use-copilot-cli)

> **One-click setup:** Click the VS Code badge for automatic configuration (requires `uv` installed)
> **Manual setup:** See instructions below for Cursor, Claude Code, Copilot CLI, or Claude Desktop

## Features

- **azure_updates_search** – Search and filter Azure updates by keyword, category, status, date range, or GUID. Set `include_facets=True` to get taxonomy counts (product categories, products, tags, statuses). Use `limit=0` with `include_facets=True` to discover available filter values.

## Prompt Examples

Once connected to an MCP client, you can ask questions like:

1. **Get recent updates**: "Show me the 10 most recent Azure updates"
2. **Search by keyword**: "Find all Azure updates related to Kubernetes or AKS"
3. **Filter by status**: "What Azure features are currently in preview?"
4. **Check for retirements**: "Are there any upcoming Azure service retirements I should know about?"
5. **Discover categories**: "What Azure product categories and services are available in the updates?"

## Usage

### Run the MCP Server

```bash
uvx azure-updates-mcp
```

Or if installed with pip:

```bash
azure-updates-mcp
```

### Connect from Claude Desktop

Add to your Claude Desktop MCP config:

- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

**Using uvx (recommended)**

```json
{
  "mcpServers": {
    "azure-updates": {
      "command": "uvx",
      "args": ["azure-updates-mcp"]
    }
  }
}
```

**Using installed package**

```json
{
  "mcpServers": {
    "azure-updates": {
      "command": "azure-updates-mcp"
    }
  }
}
```

### Connect from Cursor

**Option 1: One-Click Install (Recommended)**

```
cursor://anysphere.cursor-deeplink/mcp/install?name=azure-updates-mcp&config=eyJjb21tYW5kIjogInV2eCIsICJhcmdzIjogWyJhenVyZS11cGRhdGVzLW1jcCJdfQ==
```

**Option 2: Manual Configuration**

Add to your Cursor MCP config:

- macOS: `~/Library/Application Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`
- Windows: `%APPDATA%\Cursor\User\globalStorage\saoudrizwan.claude-dev\settings\cline_mcp_settings.json`

### Connect from Claude Code

```bash
claude mcp add --transport stdio azure-updates -- uvx azure-updates-mcp
```

### Connect from GitHub Copilot CLI

Add to `~/.copilot/mcp-config.json`:

```json
{
  "mcpServers": {
    "azure-updates": {
      "type": "stdio",
      "command": "uvx",
      "args": ["azure-updates-mcp"]
    }
  }
}
```

## Development

```bash
pytest
ruff check src/ tests/
```

## License

MIT
