# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2025-02-01

### Changed
- Consolidate `azure_updates_summarize` and `azure_updates_list_categories` into `azure_updates_search` via `include_facets` parameter
- Inline facet parsing into `fetch_updates`, removing the separate `fetch_facets` function
- Bump version to 0.3.0

### Removed
- `azure_updates_summarize` tool (use `include_facets=True` with `azure_updates_search` instead)
- `azure_updates_list_categories` tool (use `include_facets=True, limit=0` with `azure_updates_search` instead)

## [0.2.0] - 2025-02-01

### Changed
- Migrate from RSS feed to Azure Updates JSON API, unlocking access to 9,300+ updates (vs ~100 from RSS)
- Replace `feedparser` dependency with `httpx` for direct JSON API access
- Expand `AzureUpdate` model with new fields (products, tags, dates, etc.)
- Rewire search, summarize, and categories tools to use JSON API

### Added
- Server-side full-text search and pagination support
- Faceted taxonomy (products, categories, tags, statuses with counts)
- `offset`, `product`, and `product_category` parameters to search tool

### Removed
- `feedparser` dependency

## [0.1.0] - 2025-01-31

### Added
- Initial release of azure-updates-mcp
- `azure_updates_search` tool for searching and filtering Azure updates
- `azure_updates_summarize` tool for getting statistical overview and trends
- `azure_updates_list_categories` tool for listing available Azure service categories
- Support for stdio transport (recommended for MCP clients)
- One-click install support for VS Code and Cursor
- Installation instructions for Claude Desktop, Claude Code, and GitHub Copilot CLI
