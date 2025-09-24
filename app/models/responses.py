"""Standardized response models for the API."""

from datetime import datetime

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Standardized error response model."""

    error: str = Field(..., description="Error type or code")
    detail: str = Field(..., description="Human-readable error message")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="Error timestamp"
    )


class PaginatedResponse[T](BaseModel):
    """Paginated response wrapper for list endpoints."""

    items: list[T] = Field(..., description="List of items for current page")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number (1-based)")
    size: int = Field(..., description="Number of items per page")
    has_next: bool = Field(..., description="Whether there are more pages")

    @classmethod
    def create(
        cls, items: list[T], total: int, page: int, size: int
    ) -> "PaginatedResponse[T]":
        """Create paginated response from items and pagination info."""
        return cls(
            items=items,
            total=total,
            page=page,
            size=size,
            has_next=(page * size) < total,
        )


class HealthCheck(BaseModel):
    """Health check response model."""

    status: str = Field(..., description="Overall service status")
    version: str = Field(..., description="Application version")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="Check timestamp"
    )
    services: dict = Field(
        default_factory=dict, description="Individual service status"
    )
