"""
Shared validation utilities for skills.

This module provides common validation functions to reduce code duplication
across skill implementations.

Reference: specs/technical.md (API contracts)
"""

from typing import Dict, Any, List, Optional


def validate_required_field(input_data: Dict[str, Any], field_name: str) -> None:
    """
    Validate that a required field exists in input data.
    
    Args:
        input_data: Input dictionary to validate
        field_name: Name of the required field
        
    Raises:
        ValueError: If field is missing
    """
    if field_name not in input_data:
        raise ValueError(f"Missing required field: {field_name}")


def validate_string_field(
    value: Any,
    field_name: str,
    min_length: int = 1,
    max_length: Optional[int] = None
) -> None:
    """
    Validate that a value is a non-empty string within length constraints.
    
    Args:
        value: Value to validate
        field_name: Name of the field (for error messages)
        min_length: Minimum string length
        max_length: Maximum string length (None for no limit)
        
    Raises:
        ValueError: If value is not a valid string
    """
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string")
    
    if len(value) < min_length:
        raise ValueError(f"{field_name} must be at least {min_length} character(s)")
    
    if max_length is not None and len(value) > max_length:
        raise ValueError(f"{field_name} must be at most {max_length} characters")


def validate_enum_field(
    value: Any,
    field_name: str,
    valid_values: List[str]
) -> None:
    """
    Validate that a value is one of the allowed enum values.
    
    Args:
        value: Value to validate
        field_name: Name of the field (for error messages)
        valid_values: List of valid enum values
        
    Raises:
        ValueError: If value is not in valid_values
    """
    if value not in valid_values:
        raise ValueError(f"{field_name} must be one of: {valid_values}")


def validate_list_field(
    value: Any,
    field_name: str,
    min_items: int = 1,
    max_items: Optional[int] = None,
    item_validator: Optional[callable] = None
) -> None:
    """
    Validate that a value is a list with constraints.
    
    Args:
        value: Value to validate
        field_name: Name of the field (for error messages)
        min_items: Minimum number of items
        max_items: Maximum number of items (None for no limit)
        item_validator: Optional function to validate each item
        
    Raises:
        ValueError: If value is not a valid list
    """
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list")
    
    if len(value) < min_items:
        raise ValueError(f"{field_name} must contain at least {min_items} item(s)")
    
    if max_items is not None and len(value) > max_items:
        raise ValueError(f"{field_name} must contain at most {max_items} item(s)")
    
    if item_validator:
        for item in value:
            item_validator(item)


def validate_string_list_items(value: List[Any], field_name: str) -> None:
    """
    Validate that all items in a list are strings.
    
    Args:
        value: List to validate
        field_name: Name of the field (for error messages)
        
    Raises:
        ValueError: If any item is not a string
    """
    if not all(isinstance(item, str) for item in value):
        raise ValueError(f"{field_name} must be a list of strings")
