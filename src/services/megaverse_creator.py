"""Main orchestration service for megaverse creation."""

import logging
import time
from typing import Any, Dict, List, Protocol

from src.config.settings import Settings
from src.models.astral_objects import AstralObject
from src.models.exceptions import MegaverseError
from src.services.api_client import APIClient
from src.services.goal_loader import GoalLoader
from src.services.object_factory import ObjectFactory


class ProgressObserver(Protocol):
    """Protocol for progress observers."""

    def on_start(self, total_objects: int) -> None:
        """Called when creation starts."""
        pass

    def on_progress(self, current: int, total: int, obj: AstralObject, success: bool) -> None:
        """Called after each object creation attempt."""
        pass

    def on_complete(self, results: Dict[str, Any]) -> None:
        """Called when creation is complete."""
        pass


class ConsoleProgressObserver:
    """Console-based progress observer."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

    def on_start(self, total_objects: int) -> None:
        """Called when creation starts."""
        self.logger.info(f"🌌 Starting megaverse creation with {total_objects} objects")

    def on_progress(self, current: int, total: int, obj: AstralObject, success: bool) -> None:
        """Called after each object creation attempt."""
        status = "✅" if success else "❌"
        self.logger.info(f"   [{current:3d}/{total}] {status} {obj}")

    def on_complete(self, results: Dict[str, Any]) -> None:
        """Called when creation is complete."""
        self.logger.info("🎉 Megaverse creation complete!")
        self.logger.info(f"   ✅ Successful: {results['successful']}")
        self.logger.info(f"   ❌ Failed: {results['failed']}")
        self.logger.info(f"   📊 Total: {results['total']}")


class MegaverseCreator:
    """Main service for orchestrating megaverse creation."""

    def __init__(
        self,
        api_client: APIClient,
        goal_loader: GoalLoader,
        object_factory: ObjectFactory,
        settings: Settings,
    ):
        """
        Initialize the megaverse creator.

        Args:
            api_client: API client for making requests
            goal_loader: Service for loading goal maps
            object_factory: Factory for creating astral objects
            settings: Application settings
        """
        self.api_client = api_client
        self.goal_loader = goal_loader
        self.object_factory = object_factory
        self.settings = settings
        self.observers: List[ProgressObserver] = []
        self.logger = logging.getLogger(__name__)

    def add_observer(self, observer: ProgressObserver) -> None:
        """Add a progress observer."""
        self.observers.append(observer)

    def remove_observer(self, observer: ProgressObserver) -> None:
        """Remove a progress observer."""
        if observer in self.observers:
            self.observers.remove(observer)

    def create_from_file(self, goal_file: str) -> Dict[str, Any]:
        """
        Create megaverse from a goal map file.

        Args:
            goal_file: Path to the goal map file

        Returns:
            Dictionary with creation results

        Raises:
            MegaverseError: If creation fails
        """
        try:
            # Load goal map
            goal_map = self.goal_loader.load_from_file(goal_file)

            # Get map statistics
            stats = self.goal_loader.get_map_statistics(goal_map)
            self.logger.info(f"Goal map statistics: {stats}")

            # Create objects
            objects = self.object_factory.create_from_map(goal_map)

            # Order objects optimally
            ordered_objects = self.object_factory.get_creation_order(objects)

            # Create the megaverse
            return self._create_objects(ordered_objects)

        except Exception as e:
            raise MegaverseError(f"Failed to create megaverse from file {goal_file}: {e}")

    def create_from_api(self, candidate_id: str) -> Dict[str, Any]:
        """
        Create megaverse from API goal map.

        Args:
            candidate_id: The candidate ID

        Returns:
            Dictionary with creation results

        Raises:
            MegaverseError: If creation fails
        """
        try:
            # Load goal map from API
            goal_map = self.goal_loader.load_from_api(self.api_client, candidate_id)

            # Get map statistics
            stats = self.goal_loader.get_map_statistics(goal_map)
            self.logger.info(f"Goal map statistics: {stats}")

            # Create objects
            objects = self.object_factory.create_from_map(goal_map)

            # Order objects optimally
            ordered_objects = self.object_factory.get_creation_order(objects)

            # Create the megaverse
            return self._create_objects(ordered_objects)

        except Exception as e:
            raise MegaverseError(f"Failed to create megaverse from API: {e}")

    def delete_all(self, candidate_id: str) -> Dict[str, Any]:
        """
        Delete all objects from the current megaverse.

        Args:
            candidate_id: The candidate ID

        Returns:
            Dictionary with deletion results

        Raises:
            MegaverseError: If deletion fails
        """
        try:
            # Get current map
            current_map_data = self.api_client.get_current_map(candidate_id)
            if not current_map_data or "map" not in current_map_data:
                self.logger.info("No current map found, nothing to delete")
                return {"successful": 0, "failed": 0, "total": 0}

            # Create objects from current map
            objects = self.object_factory.create_from_map(current_map_data["map"])

            # Delete objects (reverse order of creation)
            objects.reverse()

            return self._delete_objects(objects, candidate_id)

        except Exception as e:
            raise MegaverseError(f"Failed to delete megaverse: {e}")

    def _create_objects(self, objects: List[AstralObject]) -> Dict[str, Any]:
        """
        Create astral objects via API.

        Args:
            objects: List of objects to create

        Returns:
            Dictionary with creation results
        """
        results = {"successful": 0, "failed": 0, "total": len(objects)}

        # Notify observers
        for observer in self.observers:
            observer.on_start(len(objects))

        for i, obj in enumerate(objects, 1):
            try:
                success = self.api_client.create_object(obj, self.settings.candidate_id)
                if success:
                    results["successful"] += 1
                else:
                    results["failed"] += 1

                # Notify observers
                for observer in self.observers:
                    observer.on_progress(i, len(objects), obj, success)

            except Exception as e:
                results["failed"] += 1
                self.logger.error(f"Failed to create {obj}: {e}")

                # Notify observers
                for observer in self.observers:
                    observer.on_progress(i, len(objects), obj, False)

            # Add delay between requests
            if i < len(objects) and self.settings.request_delay > 0:
                time.sleep(self.settings.request_delay)

        # Notify observers
        for observer in self.observers:
            observer.on_complete(results)

        return results

    def _delete_objects(self, objects: List[AstralObject], candidate_id: str) -> Dict[str, Any]:
        """
        Delete astral objects via API.

        Args:
            objects: List of objects to delete
            candidate_id: The candidate ID

        Returns:
            Dictionary with deletion results
        """
        results = {"successful": 0, "failed": 0, "total": len(objects)}

        # Notify observers
        for observer in self.observers:
            observer.on_start(len(objects))

        for i, obj in enumerate(objects, 1):
            try:
                success = self.api_client.delete_object(obj, candidate_id)
                if success:
                    results["successful"] += 1
                else:
                    results["failed"] += 1

                # Notify observers
                for observer in self.observers:
                    observer.on_progress(i, len(objects), obj, success)

            except Exception as e:
                results["failed"] += 1
                self.logger.error(f"Failed to delete {obj}: {e}")

                # Notify observers
                for observer in self.observers:
                    observer.on_progress(i, len(objects), obj, False)

            # Add delay between requests
            if i < len(objects) and self.settings.request_delay > 0:
                time.sleep(self.settings.request_delay)

        # Notify observers
        for observer in self.observers:
            observer.on_complete(results)

        return results

    def preview_creation(self, goal_file: str) -> Dict[str, Any]:
        """
        Preview what would be created without actually creating objects.

        Args:
            goal_file: Path to the goal map file

        Returns:
            Dictionary with preview information
        """
        try:
            # Load goal map
            goal_map = self.goal_loader.load_from_file(goal_file)

            # Get map statistics
            stats = self.goal_loader.get_map_statistics(goal_map)

            # Create objects (but don't send to API)
            objects = self.object_factory.create_from_map(goal_map)

            # Group objects by type
            groups = self.object_factory.group_by_type(objects)

            # Calculate estimated time
            estimated_time = len(objects) * self.settings.request_delay

            return {
                "map_stats": stats,
                "objects": objects,
                "groups": groups,
                "estimated_time_seconds": estimated_time,
                "estimated_time_minutes": estimated_time / 60,
            }

        except Exception as e:
            raise MegaverseError(f"Failed to preview creation: {e}")
