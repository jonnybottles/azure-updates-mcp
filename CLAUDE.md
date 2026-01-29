# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

```bash
pip install -e ".[dev]"              # Install with dev dependencies
python -m azure_updates_mcp.server   # Run server (default: stdio transport)
MCP_TRANSPORT=http python -m azure_updates_mcp.server  # Run as HTTP server
python -m pytest tests/ -v           # Run all tests
python -m pytest tests/test_tools.py::test_ping_returns_status  # Run single test
ruff check src/ tests/               # Lint
```

Environment variables:
- `MCP_TRANSPORT` (default: stdio) - Set to "http" for HTTP transport
- `MCP_HOST` (default: 0.0.0.0) - HTTP server host
- `MCP_PORT` (default: 8000) - HTTP server port

## Architecture

MCP server using FastMCP v2 with stdio (default) or HTTP transport. Fetches Azure Updates from Microsoft's RSS feed.

**Data flow**: `server.py` registers tools → tools call `feeds/azure_rss.py` → returns `models/AzureUpdate` objects

**Adding new tools**: Create file in `tools/`, define async function with type hints, import and register with `mcp.tool()` in `server.py`

## RSS Feed

- URL: `https://www.microsoft.com/releasecommunications/api/v2/azure/rss`
- Status values extracted from titles: `[Launched]`, `[In preview]`, `[In development]`, `[Retirements]`
- Categories include service names (e.g., "Azure Kubernetes Service (AKS)") and feature areas (e.g., "Compute", "Networking")

## Container

```bash
docker build -t azure-updates-mcp .
docker run -p 8000:8000 -e MCP_TRANSPORT=http azure-updates-mcp
```

## Deploying to Azure Container Apps

### Environment Variables

Configure the following environment variables in Azure Container Apps:
- `MCP_TRANSPORT=http` (required - enables HTTP transport)
- `MCP_HOST=0.0.0.0` (optional, default is 0.0.0.0)
- `MCP_PORT=8000` (optional, default is 8000)

### Container Configuration

- **Image**: Push your Docker image to Azure Container Registry
- **Ingress**: Enable ingress on port 8000
- **Target port**: 8000
- **Transport**: HTTP
- **MCP endpoint**: `https://your-app.azurecontainerapps.io/mcp`

### MCP Client Configuration

Add both local (stdio) and cloud (HTTP) servers to your MCP config:

```json
{
  "servers": {
    "azure-updates": {
      "type": "stdio",
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "c:/Users/jonbutler/code/azure-updates-mcp",
        "azure-updates-mcp"
      ]
    },
    "azure-updates-cloud": {
      "type": "http",
      "url": "https://your-container-app.azurecontainerapps.io/mcp"
    }
  }
}
```

This gives you:
- **azure-updates**: Local development server (stdio, auto-started)
- **azure-updates-cloud**: Cloud-hosted server (HTTP, always available)

### Deployment Steps

1. Build and push container image to Azure Container Registry
2. Create Azure Container App with the image
3. Configure environment variables (set `MCP_TRANSPORT=http`)
4. Enable ingress on port 8000
5. Get the app URL and update your MCP config with the cloud endpoint
6. Test with: `curl https://your-app.azurecontainerapps.io/mcp`
