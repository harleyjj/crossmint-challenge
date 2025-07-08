"""Goal map loading and parsing service."""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List

from src.models.exceptions import GoalMapError
from src.utils.validators import validate_goal_map


class GoalLoader:
    """Service for loading and parsing goal maps."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

    def load_from_file(self, filename: str) -> List[List[str]]:
        """
        Load goal map from JSON file.

        Args:
            filename: Path to the goal map file

        Returns:
            The goal map as a 2D list

        Raises:
            GoalMapError: If the file cannot be loaded or parsed
        """
        try:
            file_path = Path(filename)
            if not file_path.exists():
                raise GoalMapError(f"Goal map file not found: {filename}")

            with open(file_path, "r") as f:
                data = json.load(f)

            if "goal" not in data:
                raise GoalMapError(f"'goal' key not found in {filename}")

            goal_map = data["goal"]

            # Validate the goal map structure
            validate_goal_map(goal_map)

            self.logger.info(
                f"Successfully loaded goal map from {filename} ({len(goal_map)}x{len(goal_map[0])})"
            )
            return goal_map  # type: ignore[no-any-return]

        except json.JSONDecodeError as e:
            raise GoalMapError(f"Invalid JSON in {filename}: {e}")
        except FileNotFoundError:
            raise GoalMapError(f"Goal map file not found: {filename}")
        except Exception as e:
            raise GoalMapError(f"Error loading goal map from {filename}: {e}")

    def load_from_api(self, api_client: Any, candidate_id: str) -> List[List[str]]:
        """
        Load goal map from API.

        Args:
            api_client: API client instance
            candidate_id: The candidate ID

        Returns:
            The goal map as a 2D list

        Raises:
            GoalMapError: If the API request fails
        """
        try:
            data = api_client.get_goal_map(candidate_id)

            if not data or "goal" not in data:
                raise GoalMapError("Invalid goal map data from API")

            goal_map = data["goal"]

            # Validate the goal map structure
            validate_goal_map(goal_map)

            self.logger.info(
                f"Successfully loaded goal map from API ({len(goal_map)}x{len(goal_map[0])})"
            )
            return goal_map  # type: ignore[no-any-return]

        except Exception as e:
            raise GoalMapError(f"Error loading goal map from API: {e}")

    def save_to_file(self, goal_map: List[List[str]], filename: str) -> None:
        """
        Save goal map to JSON file.

        Args:
            goal_map: The goal map to save
            filename: Path to save the file

        Raises:
            GoalMapError: If the file cannot be saved
        """
        try:
            validate_goal_map(goal_map)

            data = {"goal": goal_map}

            with open(filename, "w") as f:
                json.dump(data, f, indent=2)

            self.logger.info(f"Successfully saved goal map to {filename}")

        except Exception as e:
            raise GoalMapError(f"Error saving goal map to {filename}: {e}")

    def get_map_statistics(self, goal_map: List[List[str]]) -> Dict[str, Any]:
        """
        Get statistics about the goal map.

        Args:
            goal_map: The goal map to analyze

        Returns:
            Dictionary containing map statistics
        """
        stats: Dict[str, Any] = {
            "dimensions": {"rows": len(goal_map), "columns": len(goal_map[0]) if goal_map else 0},
            "total_cells": len(goal_map) * len(goal_map[0]) if goal_map else 0,
            "object_counts": {},
            "space_count": 0,
        }

        for row in goal_map:
            for cell in row:
                if cell == "SPACE":
                    stats["space_count"] += 1
                else:
                    stats["object_counts"][cell] = stats["object_counts"].get(cell, 0) + 1

        # Calculate object type summaries
        stats["type_counts"] = {
            "POLYANET": stats["object_counts"].get("POLYANET", 0),
            "SOLOON": sum(
                count
                for obj_type, count in stats["object_counts"].items()
                if obj_type.endswith("_SOLOON")
            ),
            "COMETH": sum(
                count
                for obj_type, count in stats["object_counts"].items()
                if obj_type.endswith("_COMETH")
            ),
        }

        stats["total_objects"] = sum(stats["type_counts"].values())

        return stats
