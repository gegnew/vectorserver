"""Base model with common validation and functionality."""

import json
from datetime import UTC, datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator


class TimestampedModel(BaseModel):
    """Base model with timestamps for all entities."""

    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default=datetime.now(UTC))
    updated_at: datetime | None = None


class BaseEntityModel(TimestampedModel):
    """Base model for entities with common metadata field and validation."""

    metadata: dict | None = None

    @field_validator("metadata", mode="before")
    @classmethod
    def validate_metadata(cls, value: str | dict | None) -> dict | None:
        """Convert string JSON to dict or return None if empty."""
        if value is None:
            return None
        if isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON in metadata: {e}") from e
        return value
