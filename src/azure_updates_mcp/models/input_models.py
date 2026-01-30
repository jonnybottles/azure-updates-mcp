"""Input models for MCP tool parameters."""

from typing import Literal

from pydantic import BaseModel, Field

# Valid status values from the Azure Updates feed
StatusType = Literal["Launched", "In preview", "In development", "Retirements"]


class SearchInput(BaseModel):
    """Input parameters for azure_updates_search tool."""

    query: str | None = Field(
        None,
        description="Keyword to match against title and description (case-insensitive)",
    )
    category: str | None = Field(
        None,
        description="Category to filter by (case-insensitive partial match, e.g. 'AKS' matches 'Azure Kubernetes Service (AKS)')",
    )
    status: StatusType | None = Field(
        None,
        description="Status filter. Valid values: Launched, In preview, In development, Retirements",
    )
    start_date: str | None = Field(
        None,
        description="Start date in ISO format (YYYY-MM-DD). Only include updates published on or after this date",
    )
    end_date: str | None = Field(
        None,
        description="End date in ISO format (YYYY-MM-DD). Only include updates published on or before this date. Defaults to today when start_date is provided",
    )
    guid: str | None = Field(
        None,
        description="Unique identifier to retrieve a single specific update. When provided, all other filters are ignored",
    )
    limit: int = Field(
        10,
        ge=1,
        le=100,
        description="Maximum number of results to return (default: 10, max: 100)",
    )


class SummarizeInput(BaseModel):
    """Input parameters for azure_updates_summarize tool."""

    weeks: int | None = Field(
        None,
        ge=1,
        le=12,
        description="Number of weeks to look back. When omitted, summarizes all available updates",
    )
    top_n: int = Field(
        10,
        ge=1,
        le=50,
        description="Number of top categories and highlighted updates to include (default: 10, max: 50)",
    )
