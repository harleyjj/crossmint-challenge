"""Input validation utilities."""

import re
from typing import List

from src.models.exceptions import ValidationError


def validate_candidate_id(candidate_id: str) -> str:
    """
    Validate candidate ID format.

    Args:
        candidate_id: The candidate ID to validate

    Returns:
        The validated candidate ID

    Raises:
        ValidationError: If the candidate ID is invalid
    """
    if not candidate_id:
        raise ValidationError("Candidate ID cannot be empty")

    if candidate_id == "YOUR_CANDIDATE_ID":
        raise ValidationError("Please set your actual candidate ID")

    # UUID format validation
    uuid_pattern = r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
    if not re.match(uuid_pattern, candidate_id):
        raise ValidationError(f"Invalid candidate ID format: {candidate_id}")

    return candidate_id


def validate_position(row: int, column: int, max_size: int = 50) -> None:
    """
    Validate position coordinates.

    Args:
        row: Row coordinate
        column: Column coordinate
        max_size: Maximum allowed coordinate value

    Raises:
        ValidationError: If coordinates are invalid
    """
    if row < 0 or column < 0:
        raise ValidationError(f"Position coordinates must be non-negative: ({row}, {column})")

    if row >= max_size or column >= max_size:
        raise ValidationError(
            f"Position coordinates exceed maximum size {max_size}: ({row}, {column})"
        )


def validate_goal_map(goal_map: List[List[str]]) -> None:
    """
    Validate goal map structure and contents.

    Args:
        goal_map: The goal map to validate

    Raises:
        ValidationError: If the goal map is invalid
    """
    if not goal_map:
        raise ValidationError("Goal map cannot be empty")

    if not all(isinstance(row, list) for row in goal_map):
        raise ValidationError("Goal map must be a list of lists")

    # Check if all rows have the same length
    row_lengths = [len(row) for row in goal_map]
    if len(set(row_lengths)) > 1:
        raise ValidationError("All rows in goal map must have the same length")

    # Validate cell contents
    for row_idx, row in enumerate(goal_map):
        for col_idx, cell in enumerate(row):
            if not isinstance(cell, str):
                raise ValidationError(f"Invalid cell type at ({row_idx}, {col_idx}): {type(cell)}")

            if cell == "SPACE" or cell == "POLYANET":
                continue

            if cell.endswith("_SOLOON") or cell.endswith("_COMETH"):
                continue

            raise ValidationError(f"Invalid cell value at ({row_idx}, {col_idx}): {cell}")


def validate_color(color: str) -> str:
    """
    Validate SOLoon color.

    Args:
        color: The color to validate

    Returns:
        The validated color in lowercase

    Raises:
        ValidationError: If the color is invalid
    """
    if not color:
        raise ValidationError("Color cannot be empty")

    valid_colors = ["red", "blue", "purple", "white"]
    color_lower = color.lower()

    if color_lower not in valid_colors:
        raise ValidationError(f"Invalid color: {color}. Valid colors: {valid_colors}")

    return color_lower


def validate_direction(direction: str) -> str:
    """
    Validate comETH direction.

    Args:
        direction: The direction to validate

    Returns:
        The validated direction in lowercase

    Raises:
        ValidationError: If the direction is invalid
    """
    if not direction:
        raise ValidationError("Direction cannot be empty")

    valid_directions = ["up", "down", "left", "right"]
    direction_lower = direction.lower()

    if direction_lower not in valid_directions:
        raise ValidationError(
            f"Invalid direction: {direction}. Valid directions: {valid_directions}"
        )

    return direction_lower
