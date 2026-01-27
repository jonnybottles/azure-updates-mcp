# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

```bash
pip install -e ".[dev]"              # Install with dev dependencies
python -m azure_updates_mcp.server   # Run server (default: http://0.0.0.0:8000/mcp)
python -m pytest tests/ -v           # Run all tests
python -m pytest tests/test_tools.py::test_ping_returns_status  # Run single test
ruff check src/ tests/               # Lint
```

Environment variables: `MCP_HOST` (default: 0.0.0.0), `MCP_PORT` (default: 8000)

## Architecture

Remote MCP server using FastMCP v2 with HTTP transport. Fetches Azure Updates from Microsoft's RSS feed.

**Data flow**: `server.py` registers tools → tools call `feeds/azure_rss.py` → returns `models/AzureUpdate` objects

**Adding new tools**: Create file in `tools/`, define async function with type hints, import and register with `mcp.tool()` in `server.py`

## RSS Feed

- URL: `https://www.microsoft.com/releasecommunications/api/v2/azure/rss`
- Status values extracted from titles: `[Launched]`, `[In preview]`, `[In development]`, `[Retirements]`
- Categories include service names (e.g., "Azure Kubernetes Service (AKS)") and feature areas (e.g., "Compute", "Networking")

## Container

```bash
docker build -t azure-updates-mcp .
docker run -p 8000:8000 azure-updates-mcp
```
