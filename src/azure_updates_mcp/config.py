"""Configuration management for the Azure Updates MCP server."""

import os
from datetime import timedelta


class Config:
    """Centralized configuration for the Azure Updates MCP server.

    All configuration values can be overridden via environment variables.
    """

    # RSS Feed Configuration
    AZURE_RSS_URL: str = os.getenv(
        "AZURE_RSS_URL",
        "https://www.microsoft.com/releasecommunications/api/v2/azure/rss",
    )
    RSS_TIMEOUT: float = float(os.getenv("AZURE_RSS_TIMEOUT", "30.0"))

    # Cache Configuration
    CACHE_TTL_MINUTES: int = int(os.getenv("AZURE_CACHE_TTL_MINUTES", "5"))
    CACHE_TTL: timedelta = timedelta(minutes=CACHE_TTL_MINUTES)

    # Server Transport Configuration
    MCP_TRANSPORT: str = os.getenv("MCP_TRANSPORT", "stdio")
    MCP_HOST: str = os.getenv("MCP_HOST", "0.0.0.0")
    MCP_PORT: int = int(os.getenv("MCP_PORT", "8000"))

    @classmethod
    def validate(cls) -> None:
        """Validate configuration values on startup.

        Raises:
            ValueError: If any configuration value is invalid.
        """
        if cls.RSS_TIMEOUT <= 0:
            raise ValueError(f"AZURE_RSS_TIMEOUT must be positive, got {cls.RSS_TIMEOUT}")

        if cls.CACHE_TTL_MINUTES <= 0:
            raise ValueError(f"AZURE_CACHE_TTL_MINUTES must be positive, got {cls.CACHE_TTL_MINUTES}")

        if cls.MCP_PORT < 1 or cls.MCP_PORT > 65535:
            raise ValueError(f"MCP_PORT must be between 1-65535, got {cls.MCP_PORT}")

        if cls.MCP_TRANSPORT not in ("stdio", "http"):
            raise ValueError(f"MCP_TRANSPORT must be 'stdio' or 'http', got {cls.MCP_TRANSPORT}")


# Validate configuration on module import
Config.validate()
