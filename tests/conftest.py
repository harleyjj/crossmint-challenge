"""Test configuration and fixtures."""

import json
from unittest.mock import MagicMock, Mock

import pytest

from src.config.settings import Settings
from src.models.astral_objects import Cometh, Polyanet, Position, Soloon


@pytest.fixture
def test_settings():
    """Provide test settings."""
    return Settings(
        candidate_id="test-candidate-id",
        api_base_url="https://test.api.com",
        request_delay=0.1,
        max_retries=2,
        goal_file="test_goal.json",
        log_level="DEBUG",
    )


@pytest.fixture
def sample_goal_map():
    """Provide a sample goal map for testing."""
    return [
        ["SPACE", "POLYANET", "SPACE"],
        ["BLUE_SOLOON", "SPACE", "RIGHT_COMETH"],
        ["SPACE", "RED_SOLOON", "SPACE"],
    ]


@pytest.fixture
def sample_goal_data(sample_goal_map):
    """Provide sample goal data in JSON format."""
    return {"goal": sample_goal_map}


@pytest.fixture
def sample_positions():
    """Provide sample positions for testing."""
    return [Position(0, 0), Position(1, 1), Position(2, 2)]


@pytest.fixture
def sample_polyanet():
    """Provide a sample Polyanet object."""
    return Polyanet(Position(1, 1))


@pytest.fixture
def sample_soloon():
    """Provide a sample Soloon object."""
    return Soloon(Position(0, 1), "blue")


@pytest.fixture
def sample_cometh():
    """Provide a sample Cometh object."""
    return Cometh(Position(2, 1), "right")


@pytest.fixture
def sample_objects(sample_polyanet, sample_soloon, sample_cometh):
    """Provide a list of sample astral objects."""
    return [sample_polyanet, sample_soloon, sample_cometh]


@pytest.fixture
def mock_api_client():
    """Provide a mock API client."""
    mock = Mock()
    mock.create_object.return_value = True
    mock.delete_object.return_value = True
    mock.get_current_map.return_value = {"map": [["SPACE", "POLYANET", "SPACE"]]}
    mock.get_goal_map.return_value = {"goal": [["SPACE", "POLYANET", "SPACE"]]}
    return mock


@pytest.fixture
def mock_requests_session():
    """Provide a mock requests session."""
    mock = Mock()
    mock.post.return_value.status_code = 200
    mock.post.return_value.json.return_value = {"success": True}
    mock.get.return_value.status_code = 200
    mock.get.return_value.json.return_value = {"goal": [["SPACE", "POLYANET", "SPACE"]]}
    mock.delete.return_value.status_code = 200
    return mock


@pytest.fixture
def temp_goal_file(tmp_path, sample_goal_data):
    """Create a temporary goal file for testing."""
    goal_file = tmp_path / "test_goal.json"
    with open(goal_file, "w") as f:
        json.dump(sample_goal_data, f)
    return str(goal_file)


@pytest.fixture
def invalid_goal_file(tmp_path):
    """Create an invalid goal file for testing."""
    goal_file = tmp_path / "invalid_goal.json"
    with open(goal_file, "w") as f:
        f.write("invalid json content")
    return str(goal_file)
