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

### Run locally

```bash
python -m azure_updates_mcp.server
```

The server starts on `http://0.0.0.0:8000` by default. Configure via environment variables:

- `MCP_HOST` - Bind address (default: `0.0.0.0`)
- `MCP_PORT` - Port number (default: `8000`)

### Connect from Claude Code

```bash
claude mcp add --transport http azure-updates http://localhost:8000/mcp
```

### Docker

```bash
# Build
docker build -t azure-updates-mcp .

# Run
docker run -p 8000:8000 azure-updates-mcp
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
