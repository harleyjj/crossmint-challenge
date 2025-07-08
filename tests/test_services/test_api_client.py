"""Tests for API client service."""

from unittest.mock import MagicMock, Mock, patch

import pytest
import requests

from src.models.astral_objects import Cometh, Polyanet, Position, Soloon
from src.models.exceptions import APIError
from src.services.api_client import APIClient


class TestAPIClient:
    """Test APIClient class."""

    def setup_method(self):
        """Setup test client."""
        self.client = APIClient("https://test.api.com", max_retries=2)

    def test_client_initialization(self):
        """Test API client initialization."""
        assert self.client.base_url == "https://test.api.com"
        assert self.client.max_retries == 2
        assert self.client.session is not None

    def test_base_url_normalization(self):
        """Test base URL normalization (trailing slash removal)."""
        client = APIClient("https://test.api.com/")
        assert client.base_url == "https://test.api.com"

    @patch("requests.Session.post")
    def test_create_object_success(self, mock_post):
        """Test successful object creation."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        # Create test object
        polyanet = Polyanet(Position(1, 2))

        # Test creation
        result = self.client.create_object(polyanet, "test-candidate")

        # Verify result
        assert result is True
        mock_post.assert_called_once()

        # Verify call parameters
        args, kwargs = mock_post.call_args
        assert args[0] == "https://test.api.com/polyanets"
        assert kwargs["json"] == {"candidateId": "test-candidate", "row": 1, "column": 2}

    @patch("requests.Session.post")
    def test_create_object_api_error(self, mock_post):
        """Test API error during object creation."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_post.return_value = mock_response

        # Create test object
        polyanet = Polyanet(Position(1, 2))

        # Test creation should raise APIError
        with pytest.raises(APIError) as exc_info:
            self.client.create_object(polyanet, "test-candidate")

        # Verify error details
        error = exc_info.value
        assert error.status_code == 400
        assert error.response_text == "Bad Request"
        assert "Failed to create POLYANET" in str(error)

    @patch("requests.Session.post")
    def test_create_object_network_error(self, mock_post):
        """Test network error during object creation."""
        # Setup mock to raise network error
        mock_post.side_effect = requests.exceptions.ConnectionError("Network error")

        # Create test object
        polyanet = Polyanet(Position(1, 2))

        # Test creation should raise APIError
        with pytest.raises(APIError) as exc_info:
            self.client.create_object(polyanet, "test-candidate")

        # Verify error message
        assert "Network error" in str(exc_info.value)

    @patch("requests.Session.delete")
    def test_delete_object_success(self, mock_delete):
        """Test successful object deletion."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_delete.return_value = mock_response

        # Create test object
        soloon = Soloon(Position(0, 1), "blue")

        # Test deletion
        result = self.client.delete_object(soloon, "test-candidate")

        # Verify result
        assert result is True
        mock_delete.assert_called_once()

        # Verify call parameters
        args, kwargs = mock_delete.call_args
        assert args[0] == "https://test.api.com/soloons"
        assert kwargs["json"] == {
            "candidateId": "test-candidate",
            "row": 0,
            "column": 1,
            "color": "blue",
        }

    @patch("requests.Session.get")
    def test_get_current_map_success(self, mock_get):
        """Test successful current map retrieval."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"map": [["SPACE", "POLYANET"]]}
        mock_get.return_value = mock_response

        # Test map retrieval
        result = self.client.get_current_map("test-candidate")

        # Verify result
        assert result == {"map": [["SPACE", "POLYANET"]]}
        mock_get.assert_called_once_with("https://test.api.com/map/test-candidate")

    @patch("requests.Session.get")
    def test_get_goal_map_success(self, mock_get):
        """Test successful goal map retrieval."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"goal": [["SPACE", "POLYANET"]]}
        mock_get.return_value = mock_response

        # Test goal map retrieval
        result = self.client.get_goal_map("test-candidate")

        # Verify result
        assert result == {"goal": [["SPACE", "POLYANET"]]}
        mock_get.assert_called_once_with("https://test.api.com/map/test-candidate/goal")

    @patch("requests.Session.get")
    def test_get_map_error(self, mock_get):
        """Test error during map retrieval."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_get.return_value = mock_response

        # Test map retrieval should raise APIError
        with pytest.raises(APIError) as exc_info:
            self.client.get_current_map("test-candidate")

        # Verify error details
        error = exc_info.value
        assert error.status_code == 404
        assert error.response_text == "Not Found"

    def test_close_session(self):
        """Test session cleanup."""
        # Mock the session
        mock_session = Mock()
        self.client.session = mock_session

        # Close client
        self.client.close()

        # Verify session was closed
        mock_session.close.assert_called_once()

    def test_different_object_types(self):
        """Test API client with different object types."""
        objects = [
            Polyanet(Position(0, 0)),
            Soloon(Position(1, 1), "red"),
            Cometh(Position(2, 2), "left"),
        ]

        expected_endpoints = ["polyanets", "soloons", "comeths"]

        for obj, expected_endpoint in zip(objects, expected_endpoints):
            with patch("requests.Session.post") as mock_post:
                mock_response = Mock()
                mock_response.status_code = 200
                mock_post.return_value = mock_response

                self.client.create_object(obj, "test-candidate")

                # Verify correct endpoint was called
                args, kwargs = mock_post.call_args
                assert args[0] == f"https://test.api.com/{expected_endpoint}"
