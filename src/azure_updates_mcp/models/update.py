"""Pydantic models for Azure Updates."""

from datetime import datetime

from pydantic import BaseModel, Field


class AzureUpdate(BaseModel):
    """Represents a single Azure service update from the JSON API."""

    id: str = Field(description="Unique identifier for the update")
    title: str = Field(description="Update headline")
    link: str = Field(description="URL to the full update page")
    description: str = Field(description="Summary text of the update")
    status: str | None = Field(
        default=None,
        description="Update status: Launched, In preview, In development, or Retirements",
    )

    # Date fields
    created: datetime = Field(description="Creation timestamp")
    modified: datetime | None = Field(default=None, description="Last modified timestamp")

    # Taxonomy fields from JSON API
    products: list[str] = Field(default_factory=list, description="Product names")
    product_categories: list[str] = Field(
        default_factory=list, description="Product category names"
    )
    tags: list[str] = Field(default_factory=list, description="Tag labels")

    # Additional date fields
    general_availability_date: str | None = Field(
        default=None, description="GA date string from API"
    )
    preview_availability_date: str | None = Field(
        default=None, description="Preview availability date string"
    )
    private_preview_availability_date: str | None = Field(
        default=None, description="Private preview availability date string"
    )

    # Backward-compat properties
    @property
    def guid(self) -> str:
        """Backward-compatible alias for id."""
        return self.id

    @property
    def pub_date(self) -> datetime:
        """Backward-compatible alias for created."""
        return self.created

    @property
    def categories(self) -> list[str]:
        """Backward-compatible merged list of products + product_categories + tags."""
        return self.products + self.product_categories + self.tags

    def to_dict(self) -> dict:
        """Convert to dictionary with ISO formatted dates."""
        result = {
            # New fields
            "id": self.id,
            "title": self.title,
            "link": self.link,
            "description": self.description,
            "status": self.status,
            "created": self.created.isoformat(),
            "modified": self.modified.isoformat() if self.modified else None,
            "products": self.products,
            "product_categories": self.product_categories,
            "tags": self.tags,
            "general_availability_date": self.general_availability_date,
            "preview_availability_date": self.preview_availability_date,
            "private_preview_availability_date": self.private_preview_availability_date,
            # Backward-compat keys
            "guid": self.id,
            "pub_date": self.created.isoformat(),
            "categories": self.categories,
        }
        return result
