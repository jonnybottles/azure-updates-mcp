# Installation Reference

Quick reference for installing azure-updates-mcp across different MCP clients.

## Prerequisites

- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) installed (recommended)

## PyPI Package

After publishing to PyPI, the package will be available at:
https://pypi.org/project/azure-updates-mcp/

## Installation Commands

### Direct Installation

**Using uvx (recommended - no installation needed):**
```bash
uvx azure-updates-mcp
```

**Using pip:**
```bash
pip install azure-updates-mcp
azure-updates-mcp
```

**From source:**
```bash
git clone https://github.com/YOUR-USERNAME/azure-updates-mcp.git
cd azure-updates-mcp
pip install -e .
azure-updates-mcp
```

## MCP Client Configurations

### Claude Desktop

**Config file location:**
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

**Recommended configuration (using uvx):**
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

**Alternative (if installed with pip):**
```json
{
  "mcpServers": {
    "azure-updates": {
      "command": "azure-updates-mcp"
    }
  }
}
```

### Claude Code

**Recommended (using uvx):**
```bash
claude mcp add --transport stdio azure-updates -- uvx azure-updates-mcp
```

**Alternative (if installed):**
```bash
claude mcp add --transport stdio azure-updates -- azure-updates-mcp
```

**List installed servers:**
```bash
claude mcp list
```

**Remove server:**
```bash
claude mcp remove azure-updates
```

### VS Code

**One-click install:**
- Click the VS Code badge in README
- Or visit: https://vscode.dev/redirect/mcp/install?name=azure-updates-mcp&config=%7B%22type%22%3A%20%22stdio%22%2C%20%22command%22%3A%20%22uvx%22%2C%20%22args%22%3A%20%5B%22azure-updates-mcp%22%5D%7D

**Manual configuration:**
Add to VS Code MCP settings:
```json
{
  "azure-updates-mcp": {
    "type": "stdio",
    "command": "uvx",
    "args": ["azure-updates-mcp"]
  }
}
```

### Cursor

**One-click install:**
- Click the Cursor badge in README
- Or visit: https://vscode.dev/redirect/mcp/install?name=azure-updates-mcp&config=%7B%22type%22%3A%20%22stdio%22%2C%20%22command%22%3A%20%22uvx%22%2C%20%22args%22%3A%20%5B%22azure-updates-mcp%22%5D%7D

**Manual configuration:**
Same as VS Code (Cursor uses VS Code's configuration format)

### GitHub Copilot CLI

**Config file location:**
- `~/.copilot/mcp-config.json`

**Recommended configuration:**
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

**Alternative (if installed):**
```json
{
  "mcpServers": {
    "azure-updates": {
      "type": "stdio",
      "command": "azure-updates-mcp"
    }
  }
}
```

## Development Installation

For contributing or development:

```bash
# Clone repository
git clone https://github.com/YOUR-USERNAME/azure-updates-mcp.git
cd azure-updates-mcp

# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linter
ruff check src/ tests/

# Run server
azure-updates-mcp
```

## Troubleshooting

### Command not found: uvx
Install uv:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh  # macOS/Linux
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"  # Windows
```

### Package not found on PyPI
The package must be published to PyPI first. See PUBLISHING.md.

### Server not connecting
1. Check server is running: `uvx azure-updates-mcp`
2. Verify config file syntax (valid JSON)
3. Restart MCP client (Claude Desktop, VS Code, etc.)
4. Check client logs for errors

### Permission denied
On macOS/Linux, you may need to make the script executable:
```bash
chmod +x $(which azure-updates-mcp)
```

## Version Management

**Check installed version:**
```bash
pip show azure-updates-mcp
```

**Install specific version:**
```bash
uvx azure-updates-mcp@0.1.0
pip install azure-updates-mcp==0.1.0
```

**Update to latest:**
```bash
pip install --upgrade azure-updates-mcp
```

## Configuration Comparison

| Client | Command | Config File | One-Click |
|--------|---------|-------------|-----------|
| Claude Desktop | `uvx azure-updates-mcp` | `claude_desktop_config.json` | ❌ |
| Claude Code | `claude mcp add ...` | `~/.claude/config.json` | ❌ |
| VS Code | `uvx azure-updates-mcp` | VS Code MCP settings | ✅ |
| Cursor | `uvx azure-updates-mcp` | Cursor MCP settings | ✅ |
| Copilot CLI | `uvx azure-updates-mcp` | `~/.copilot/mcp-config.json` | ❌ |

## Best Practices

1. **Use uvx when possible** - No installation required, always uses latest version
2. **Use pip for pinned versions** - When you need a specific version
3. **Use source install for development** - When contributing to the project
4. **Keep config simple** - Use minimal configuration that works

## Quick Start

**Fastest way to get started:**

1. Install uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`
2. Add to Claude Desktop config:
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
3. Restart Claude Desktop
4. Ask: "Show me recent Azure updates"

---

**Note:** All configurations assume the package is published to PyPI. Before publication, use local installation methods described in PUBLISHING.md.
