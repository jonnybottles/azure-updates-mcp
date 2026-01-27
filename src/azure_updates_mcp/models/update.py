"""Pydantic models for Azure Updates."""

from datetime import datetime

from pydantic import BaseModel, Field


class AzureUpdate(BaseModel):
    """Represents a single Azure service update from the RSS feed."""

    guid: str = Field(description="Unique identifier for the update")
    title: str = Field(description="Update headline")
    link: str = Field(description="URL to the full update page")
    description: str = Field(description="Summary text of the update")
    pub_date: datetime = Field(description="Publication timestamp")
    categories: list[str] = Field(default_factory=list, description="Classification tags")
    status: str | None = Field(
        default=None,
        description="Update status: Launched, In preview, In development, or Retirements",
    )

    def to_dict(self) -> dict:
        """Convert to dictionary with ISO formatted date."""
        return {
            "guid": self.guid,
            "title": self.title,
            "link": self.link,
            "description": self.description,
            "pub_date": self.pub_date.isoformat(),
            "categories": self.categories,
            "status": self.status,
        }
