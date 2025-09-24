from __future__ import annotations

from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class MetadataFilter(BaseModel):
    """Metadata filter for search queries."""

    field: str
    operator: Literal[
        "eq",
        "ne",
        "gt",
        "gte",
        "lt",
        "lte",
        "in",
        "contains",
        "starts_with",
        "ends_with",
    ]
    value: Any

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"field": "author", "operator": "eq", "value": "John Doe"}
        }
    )


class SearchText(BaseModel):
    content: str
    library_id: UUID
    index_type: Literal["ivf", "flat"] = "flat"
    metadata_filters: list[MetadataFilter] = Field(default_factory=list)
    limit: int = Field(default=5, ge=1, le=100)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "content": "machine learning algorithms",
                "library_id": "123e4567-e89b-12d3-a456-426614174000",
                "index_type": "flat",
                "metadata_filters": [
                    {"field": "created_at", "operator": "gte", "value": "2024-01-01"}
                ],
                "limit": 10,
            }
        }
    )


class SearchResult(BaseModel):
    """Search result with similarity score."""

    document: "Document"
    score: float = Field(
        ..., description="Similarity score (0-1, higher is more similar)"
    )
    matching_chunks: int = Field(
        ..., description="Number of matching chunks in this document"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "document": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "title": "Machine Learning Basics",
                    "content": "Introduction to ML...",
                },
                "score": 0.89,
                "matching_chunks": 3,
            }
        }
    )
