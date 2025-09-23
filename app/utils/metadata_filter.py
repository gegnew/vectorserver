"""Metadata filtering utilities for search operations."""

import re
from datetime import datetime
from typing import Any, Dict, List

from app.models.models import MetadataFilter


class MetadataFilterProcessor:
    """Processes metadata filters for search operations."""

    @staticmethod
    def apply_filters(items: List[Any], filters: List[MetadataFilter], metadata_field: str = "metadata") -> List[Any]:
        """Apply metadata filters to a list of items."""
        if not filters:
            return items

        filtered_items = []
        for item in items:
            if MetadataFilterProcessor._item_matches_filters(item, filters, metadata_field):
                filtered_items.append(item)
        
        return filtered_items

    @staticmethod
    def _item_matches_filters(item: Any, filters: List[MetadataFilter], metadata_field: str) -> bool:
        """Check if an item matches all the provided filters."""
        metadata = getattr(item, metadata_field, {}) or {}
        
        # Add built-in fields to metadata for filtering
        built_in_metadata = {
            "id": str(item.id),
            "created_at": item.created_at.isoformat() if hasattr(item, 'created_at') and item.created_at else None,
            "updated_at": item.updated_at.isoformat() if hasattr(item, 'updated_at') and item.updated_at else None,
        }
        
        # Add type-specific fields
        if hasattr(item, 'title'):
            built_in_metadata["title"] = item.title
        if hasattr(item, 'content'):
            built_in_metadata["content"] = item.content
        if hasattr(item, 'name'):
            built_in_metadata["name"] = item.name
        if hasattr(item, 'description'):
            built_in_metadata["description"] = item.description
        
        # Merge custom metadata with built-in metadata
        combined_metadata = {**built_in_metadata, **metadata}
        
        # All filters must match (AND logic)
        for filter_condition in filters:
            if not MetadataFilterProcessor._matches_filter(combined_metadata, filter_condition):
                return False
        
        return True

    @staticmethod
    def _matches_filter(metadata: Dict[str, Any], filter_condition: MetadataFilter) -> bool:
        """Check if metadata matches a single filter condition."""
        field_value = metadata.get(filter_condition.field)
        filter_value = filter_condition.value
        operator = filter_condition.operator

        # Handle None values
        if field_value is None:
            return operator == "ne" and filter_value is not None

        # Convert values for comparison if needed
        field_value, filter_value = MetadataFilterProcessor._normalize_values(field_value, filter_value)

        # Apply the operator
        try:
            match operator:
                case "eq":
                    return field_value == filter_value
                case "ne":
                    return field_value != filter_value
                case "gt":
                    return field_value > filter_value
                case "gte":
                    return field_value >= filter_value
                case "lt":
                    return field_value < filter_value
                case "lte":
                    return field_value <= filter_value
                case "in":
                    return field_value in filter_value if isinstance(filter_value, (list, tuple, set)) else False
                case "contains":
                    return str(filter_value).lower() in str(field_value).lower()
                case "starts_with":
                    return str(field_value).lower().startswith(str(filter_value).lower())
                case "ends_with":
                    return str(field_value).lower().endswith(str(filter_value).lower())
                case _:
                    return False
        except (TypeError, ValueError):
            # If comparison fails, filter doesn't match
            return False

    @staticmethod
    def _normalize_values(field_value: Any, filter_value: Any) -> tuple[Any, Any]:
        """Normalize values for comparison, handling type conversions."""
        # Try to parse dates
        if isinstance(filter_value, str):
            try:
                # Try to parse as ISO date
                filter_date = datetime.fromisoformat(filter_value.replace('Z', '+00:00'))
                if isinstance(field_value, str):
                    field_date = datetime.fromisoformat(field_value.replace('Z', '+00:00'))
                    return field_date, filter_date
                elif isinstance(field_value, datetime):
                    return field_value, filter_date
            except (ValueError, AttributeError):
                pass

        # Try to convert to numbers if both are numeric strings
        if isinstance(field_value, str) and isinstance(filter_value, str):
            try:
                field_float = float(field_value)
                filter_float = float(filter_value)
                return field_float, filter_float
            except ValueError:
                pass

        # Handle numeric comparisons
        if isinstance(field_value, (int, float)) and isinstance(filter_value, str):
            try:
                return field_value, float(filter_value)
            except ValueError:
                pass
        
        if isinstance(filter_value, (int, float)) and isinstance(field_value, str):
            try:
                return float(field_value), filter_value
            except ValueError:
                pass

        return field_value, filter_value

    @staticmethod
    def validate_filters(filters: List[MetadataFilter]) -> List[str]:
        """Validate metadata filters and return list of error messages."""
        errors = []
        
        for i, filter_condition in enumerate(filters):
            # Validate field name
            if not filter_condition.field or not isinstance(filter_condition.field, str):
                errors.append(f"Filter {i}: field must be a non-empty string")
            
            # Validate operator
            valid_operators = ["eq", "ne", "gt", "gte", "lt", "lte", "in", "contains", "starts_with", "ends_with"]
            if filter_condition.operator not in valid_operators:
                errors.append(f"Filter {i}: operator must be one of {valid_operators}")
            
            # Validate value for specific operators
            if filter_condition.operator == "in" and not isinstance(filter_condition.value, (list, tuple)):
                errors.append(f"Filter {i}: 'in' operator requires a list or tuple value")
        
        return errors