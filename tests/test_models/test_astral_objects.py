"""Tests for astral objects models."""

import pytest

from src.models.astral_objects import Cometh, Polyanet, Position, Soloon


class TestPosition:
    """Test Position class."""

    def test_position_creation(self):
        """Test position object creation."""
        pos = Position(row=1, column=2)
        assert pos.row == 1
        assert pos.column == 2

    def test_position_equality(self):
        """Test position equality comparison."""
        pos1 = Position(1, 2)
        pos2 = Position(1, 2)
        pos3 = Position(2, 1)

        assert pos1 == pos2
        assert pos1 != pos3


class TestPolyanet:
    """Test Polyanet class."""

    def test_polyanet_creation(self):
        """Test Polyanet object creation."""
        pos = Position(row=1, column=2)
        polyanet = Polyanet(pos)

        assert polyanet.position == pos
        assert polyanet.position.row == 1
        assert polyanet.position.column == 2

    def test_polyanet_api_endpoint(self):
        """Test Polyanet API endpoint."""
        polyanet = Polyanet(Position(0, 0))
        assert polyanet.get_api_endpoint() == "polyanets"

    def test_polyanet_object_type(self):
        """Test Polyanet object type."""
        polyanet = Polyanet(Position(0, 0))
        assert polyanet.get_object_type() == "POLYANET"

    def test_polyanet_payload(self):
        """Test Polyanet API payload."""
        polyanet = Polyanet(Position(1, 2))
        payload = polyanet.get_payload("test-candidate")

        expected = {"candidateId": "test-candidate", "row": 1, "column": 2}
        assert payload == expected

    def test_polyanet_string_representation(self):
        """Test Polyanet string representation."""
        polyanet = Polyanet(Position(1, 2))
        assert str(polyanet) == "POLYANET at (1, 2)"


class TestSoloon:
    """Test Soloon class."""

    def test_soloon_creation(self):
        """Test Soloon object creation."""
        pos = Position(row=1, column=2)
        soloon = Soloon(pos, "blue")

        assert soloon.position == pos
        assert soloon.color == "blue"

    def test_soloon_color_normalization(self):
        """Test Soloon color normalization to lowercase."""
        soloon = Soloon(Position(0, 0), "BLUE")
        assert soloon.color == "blue"

    def test_soloon_api_endpoint(self):
        """Test Soloon API endpoint."""
        soloon = Soloon(Position(0, 0), "blue")
        assert soloon.get_api_endpoint() == "soloons"

    def test_soloon_object_type(self):
        """Test Soloon object type."""
        soloon = Soloon(Position(0, 0), "blue")
        assert soloon.get_object_type() == "BLUE_SOLOON"

    def test_soloon_payload(self):
        """Test Soloon API payload."""
        soloon = Soloon(Position(1, 2), "red")
        payload = soloon.get_payload("test-candidate")

        expected = {"candidateId": "test-candidate", "row": 1, "column": 2, "color": "red"}
        assert payload == expected

    def test_soloon_string_representation(self):
        """Test Soloon string representation."""
        soloon = Soloon(Position(1, 2), "blue")
        assert str(soloon) == "BLUE_SOLOON at (1, 2)"


class TestCometh:
    """Test Cometh class."""

    def test_cometh_creation(self):
        """Test Cometh object creation."""
        pos = Position(row=1, column=2)
        cometh = Cometh(pos, "up")

        assert cometh.position == pos
        assert cometh.direction == "up"

    def test_cometh_direction_normalization(self):
        """Test Cometh direction normalization to lowercase."""
        cometh = Cometh(Position(0, 0), "UP")
        assert cometh.direction == "up"

    def test_cometh_api_endpoint(self):
        """Test Cometh API endpoint."""
        cometh = Cometh(Position(0, 0), "right")
        assert cometh.get_api_endpoint() == "comeths"

    def test_cometh_object_type(self):
        """Test Cometh object type."""
        cometh = Cometh(Position(0, 0), "left")
        assert cometh.get_object_type() == "LEFT_COMETH"

    def test_cometh_payload(self):
        """Test Cometh API payload."""
        cometh = Cometh(Position(1, 2), "down")
        payload = cometh.get_payload("test-candidate")

        expected = {"candidateId": "test-candidate", "row": 1, "column": 2, "direction": "down"}
        assert payload == expected

    def test_cometh_string_representation(self):
        """Test Cometh string representation."""
        cometh = Cometh(Position(1, 2), "right")
        assert str(cometh) == "RIGHT_COMETH at (1, 2)"


class TestAstralObjectPolymorphism:
    """Test polymorphic behavior of astral objects."""

    def test_common_interface(self):
        """Test that all astral objects implement the common interface."""
        objects = [
            Polyanet(Position(0, 0)),
            Soloon(Position(1, 1), "blue"),
            Cometh(Position(2, 2), "up"),
        ]

        for obj in objects:
            # All objects should have these methods
            assert hasattr(obj, "get_api_endpoint")
            assert hasattr(obj, "get_payload")
            assert hasattr(obj, "get_object_type")
            assert hasattr(obj, "position")

            # Methods should return expected types
            assert isinstance(obj.get_api_endpoint(), str)
            assert isinstance(obj.get_payload("test"), dict)
            assert isinstance(obj.get_object_type(), str)
            assert isinstance(obj.position, Position)
