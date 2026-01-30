"""Data models for Azure Updates."""

from .input_models import SearchInput, SummarizeInput
from .update import AzureUpdate

__all__ = ["AzureUpdate", "SearchInput", "SummarizeInput"]
