"""Entry point for running the Azure Updates MCP server as a module.

Enables 'python -m azure_updates_mcp' invocation.
"""

from .server import main

if __name__ == "__main__":
    main()
