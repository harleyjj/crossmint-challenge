"""End-to-end integration tests."""

from unittest.mock import Mock, patch

import pytest

from src.config.settings import Settings
from src.services.api_client import APIClient
from src.services.goal_loader import GoalLoader
from src.services.megaverse_creator import MegaverseCreator
from src.services.object_factory import ObjectFactory


class TestEndToEnd:
    """End-to-end integration tests."""

    def setup_method(self):
        """Setup test components."""
        self.settings = Settings(
            candidate_id="test-candidate",
            api_base_url="https://test.api.com",
            request_delay=0.1,
            max_retries=2,
        )

    @patch("requests.Session.post")
    def test_complete_workflow_from_file(self, mock_post, temp_goal_file):
        """Test complete workflow from goal file to API calls."""
        # Setup mock API responses
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        # Create services
        api_client = APIClient(self.settings.api_base_url, self.settings.max_retries)
        goal_loader = GoalLoader()
        object_factory = ObjectFactory()
        megaverse_creator = MegaverseCreator(api_client, goal_loader, object_factory, self.settings)

        # Execute creation workflow
        results = megaverse_creator.create_from_file(temp_goal_file)

        # Verify results
        assert results["successful"] > 0
        assert results["failed"] == 0
        assert results["total"] == results["successful"]

        # Verify API calls were made
        assert mock_post.call_count == results["total"]

    def test_preview_workflow(self, temp_goal_file):
        """Test preview workflow without API calls."""
        # Create services (no API client needed for preview)
        goal_loader = GoalLoader()
        object_factory = ObjectFactory()
        megaverse_creator = MegaverseCreator(None, goal_loader, object_factory, self.settings)

        # Execute preview
        preview = megaverse_creator.preview_creation(temp_goal_file)

        # Verify preview structure
        assert "map_stats" in preview
        assert "objects" in preview
        assert "groups" in preview
        assert "estimated_time_seconds" in preview
        assert "estimated_time_minutes" in preview

        # Verify statistics
        stats = preview["map_stats"]
        assert stats["dimensions"]["rows"] == 3
        assert stats["dimensions"]["columns"] == 3
        assert stats["total_objects"] > 0

    @patch("requests.Session.post")
    @patch("requests.Session.get")
    def test_workflow_with_api_goal_map(self, mock_get, mock_post):
        """Test workflow using goal map from API."""
        # Setup mock API responses
        mock_get_response = Mock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = {
            "goal": [
                ["SPACE", "POLYANET", "SPACE"],
                ["BLUE_SOLOON", "SPACE", "RIGHT_COMETH"],
                ["SPACE", "SPACE", "SPACE"],
            ]
        }
        mock_get.return_value = mock_get_response

        mock_post_response = Mock()
        mock_post_response.status_code = 200
        mock_post.return_value = mock_post_response

        # Create services
        api_client = APIClient(self.settings.api_base_url, self.settings.max_retries)
        goal_loader = GoalLoader()
        object_factory = ObjectFactory()
        megaverse_creator = MegaverseCreator(api_client, goal_loader, object_factory, self.settings)

        # Execute creation from API
        results = megaverse_creator.create_from_api("test-candidate")

        # Verify results
        assert results["successful"] == 3  # POLYANET, BLUE_SOLOON, RIGHT_COMETH
        assert results["failed"] == 0
        assert results["total"] == 3

        # Verify API calls
        assert mock_get.call_count == 1  # Goal map fetch
        assert mock_post.call_count == 3  # Object creations

    def test_error_handling_workflow(self, invalid_goal_file):
        """Test error handling in workflow."""
        # Create services
        goal_loader = GoalLoader()
        object_factory = ObjectFactory()
        megaverse_creator = MegaverseCreator(None, goal_loader, object_factory, self.settings)

        # Should raise error for invalid file
        with pytest.raises(Exception):
            megaverse_creator.create_from_file(invalid_goal_file)

    @patch("requests.Session.post")
    def test_workflow_with_observer(self, mock_post, temp_goal_file):
        """Test workflow with progress observer."""
        # Setup mock API responses
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        # Create services
        api_client = APIClient(self.settings.api_base_url, self.settings.max_retries)
        goal_loader = GoalLoader()
        object_factory = ObjectFactory()
        megaverse_creator = MegaverseCreator(api_client, goal_loader, object_factory, self.settings)

        # Create mock observer
        mock_observer = Mock()
        megaverse_creator.add_observer(mock_observer)

        # Execute workflow
        results = megaverse_creator.create_from_file(temp_goal_file)

        # Verify observer was called
        mock_observer.on_start.assert_called_once()
        mock_observer.on_complete.assert_called_once_with(results)
        assert mock_observer.on_progress.call_count == results["total"]

    def test_service_integration(self):
        """Test integration between services."""
        # Create all services
        api_client = APIClient(self.settings.api_base_url)
        goal_loader = GoalLoader()
        object_factory = ObjectFactory()

        # Test goal loader -> object factory integration
        goal_map = [["SPACE", "POLYANET", "SPACE"], ["BLUE_SOLOON", "SPACE", "RIGHT_COMETH"]]

        objects = object_factory.create_from_map(goal_map)
        assert len(objects) == 3

        # Test object factory -> API client integration (mock the actual call)
        with patch.object(api_client, "create_object", return_value=True) as mock_create:
            for obj in objects:
                result = api_client.create_object(obj, "test-candidate")
                assert result is True

            assert mock_create.call_count == 3
