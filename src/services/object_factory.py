"""Factory for creating astral objects from goal map data."""

import logging
from typing import Any, Dict, List, Optional

from src.models.astral_objects import AstralObject, Cometh, Polyanet, Position, Soloon
from src.models.exceptions import ObjectCreationError
from src.utils.validators import validate_color, validate_direction, validate_position


class ObjectFactory:
    """Factory for creating astral objects from goal map data."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

    def create_from_cell(self, cell_value: str, row: int, column: int) -> Optional[AstralObject]:
        """
        Create an astral object from a goal map cell value.

        Args:
            cell_value: The cell value from the goal map
            row: Row position
            column: Column position

        Returns:
            The created astral object, or None if it's a SPACE

        Raises:
            ObjectCreationError: If the object cannot be created
        """
        try:
            # Validate position
            validate_position(row, column)
            position = Position(row, column)

            # Handle different object types
            if cell_value == "SPACE":
                return None
            elif cell_value == "POLYANET":
                return Polyanet(position)
            elif cell_value.endswith("_SOLOON"):
                color = cell_value.replace("_SOLOON", "")
                validated_color = validate_color(color)
                return Soloon(position, validated_color)
            elif cell_value.endswith("_COMETH"):
                direction = cell_value.replace("_COMETH", "")
                validated_direction = validate_direction(direction)
                return Cometh(position, validated_direction)
            else:
                raise ObjectCreationError(f"Unknown object type: {cell_value}")

        except Exception as e:
            raise ObjectCreationError(
                f"Failed to create object from cell '{cell_value}' at ({row}, {column}): {e}"
            )

    def create_from_map(self, goal_map: List[List[str]]) -> List[AstralObject]:
        """
        Create all astral objects from a goal map.

        Args:
            goal_map: The goal map as a 2D list

        Returns:
            List of astral objects to be created

        Raises:
            ObjectCreationError: If any object cannot be created
        """
        objects = []

        try:
            for row_idx, row in enumerate(goal_map):
                for col_idx, cell in enumerate(row):
                    astral_object = self.create_from_cell(cell, row_idx, col_idx)
                    if astral_object is not None:
                        objects.append(astral_object)

            self.logger.info(f"Created {len(objects)} astral objects from goal map")
            return objects

        except Exception as e:
            raise ObjectCreationError(f"Failed to create objects from goal map: {e}")

    def create_polyanet(self, row: int, column: int) -> Polyanet:
        """
        Create a Polyanet object.

        Args:
            row: Row position
            column: Column position

        Returns:
            The created Polyanet object
        """
        validate_position(row, column)
        return Polyanet(Position(row, column))

    def create_soloon(self, row: int, column: int, color: str) -> Soloon:
        """
        Create a Soloon object.

        Args:
            row: Row position
            column: Column position
            color: Soloon color

        Returns:
            The created Soloon object
        """
        validate_position(row, column)
        validated_color = validate_color(color)
        return Soloon(Position(row, column), validated_color)

    def create_cometh(self, row: int, column: int, direction: str) -> Cometh:
        """
        Create a Cometh object.

        Args:
            row: Row position
            column: Column position
            direction: Cometh direction

        Returns:
            The created Cometh object
        """
        validate_position(row, column)
        validated_direction = validate_direction(direction)
        return Cometh(Position(row, column), validated_direction)

    def group_by_type(self, objects: List[AstralObject]) -> Dict[str, List[AstralObject]]:
        """
        Group astral objects by their type.

        Args:
            objects: List of astral objects

        Returns:
            Dictionary mapping object types to lists of objects
        """
        groups: Dict[str, List[AstralObject]] = {}

        for obj in objects:
            obj_type = obj.__class__.__name__
            if obj_type not in groups:
                groups[obj_type] = []
            groups[obj_type].append(obj)

        return groups

    def get_creation_order(self, objects: List[AstralObject]) -> List[AstralObject]:
        """
        Get objects in optimal creation order.

        According to the challenge, SOLoons must be adjacent to POLYanets,
        so we should create POLYanets first, then SOLoons, then comETHs.

        Args:
            objects: List of astral objects

        Returns:
            List of objects in creation order
        """
        polyanets = []
        soloons = []
        comeths = []

        for obj in objects:
            if isinstance(obj, Polyanet):
                polyanets.append(obj)
            elif isinstance(obj, Soloon):
                soloons.append(obj)
            elif isinstance(obj, Cometh):
                comeths.append(obj)

        # Sort each type by position for consistent ordering
        polyanets.sort(key=lambda x: (x.position.row, x.position.column))
        soloons.sort(key=lambda x: (x.position.row, x.position.column))
        comeths.sort(key=lambda x: (x.position.row, x.position.column))

        # Type-safe concatenation
        result: List[AstralObject] = []
        result.extend(polyanets)
        result.extend(soloons)
        result.extend(comeths)
        return result
