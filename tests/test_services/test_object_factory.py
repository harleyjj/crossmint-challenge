"""Tests for object factory service."""

import pytest

from src.models.astral_objects import Cometh, Polyanet, Position, Soloon
from src.models.exceptions import ObjectCreationError
from src.services.object_factory import ObjectFactory


class TestObjectFactory:
    """Test ObjectFactory class."""

    def setup_method(self):
        """Setup test factory."""
        self.factory = ObjectFactory()

    def test_create_polyanet_from_cell(self):
        """Test creating Polyanet from cell value."""
        obj = self.factory.create_from_cell("POLYANET", 1, 2)

        assert isinstance(obj, Polyanet)
        assert obj.position.row == 1
        assert obj.position.column == 2
        assert obj.get_object_type() == "POLYANET"

    def test_create_soloon_from_cell(self):
        """Test creating Soloon from cell value."""
        obj = self.factory.create_from_cell("BLUE_SOLOON", 0, 1)

        assert isinstance(obj, Soloon)
        assert obj.position.row == 0
        assert obj.position.column == 1
        assert obj.color == "blue"
        assert obj.get_object_type() == "BLUE_SOLOON"

    def test_create_cometh_from_cell(self):
        """Test creating Cometh from cell value."""
        obj = self.factory.create_from_cell("RIGHT_COMETH", 2, 0)

        assert isinstance(obj, Cometh)
        assert obj.position.row == 2
        assert obj.position.column == 0
        assert obj.direction == "right"
        assert obj.get_object_type() == "RIGHT_COMETH"

    def test_create_from_space_cell(self):
        """Test creating from SPACE cell returns None."""
        obj = self.factory.create_from_cell("SPACE", 0, 0)
        assert obj is None

    def test_create_from_invalid_cell(self):
        """Test creating from invalid cell raises error."""
        with pytest.raises(ObjectCreationError) as exc_info:
            self.factory.create_from_cell("INVALID_OBJECT", 0, 0)

        assert "Unknown object type" in str(exc_info.value)

    def test_create_from_invalid_position(self):
        """Test creating with invalid position raises error."""
        with pytest.raises(ObjectCreationError) as exc_info:
            self.factory.create_from_cell("POLYANET", -1, 0)

        assert "must be non-negative" in str(exc_info.value)

    def test_create_from_map(self):
        """Test creating objects from entire goal map."""
        goal_map = [
            ["SPACE", "POLYANET", "SPACE"],
            ["BLUE_SOLOON", "SPACE", "RIGHT_COMETH"],
            ["SPACE", "RED_SOLOON", "SPACE"],
        ]

        objects = self.factory.create_from_map(goal_map)

        # Should create 4 objects (excluding SPACE cells)
        assert len(objects) == 4

        # Verify object types and positions
        expected_objects = [(Polyanet, 0, 1), (Soloon, 1, 0), (Cometh, 1, 2), (Soloon, 2, 1)]

        for obj, (expected_type, expected_row, expected_col) in zip(objects, expected_objects):
            assert isinstance(obj, expected_type)
            assert obj.position.row == expected_row
            assert obj.position.column == expected_col

    def test_create_from_empty_map(self):
        """Test creating from empty map."""
        objects = self.factory.create_from_map([])
        assert len(objects) == 0

    def test_create_from_space_only_map(self):
        """Test creating from map with only SPACE cells."""
        goal_map = [["SPACE", "SPACE"], ["SPACE", "SPACE"]]

        objects = self.factory.create_from_map(goal_map)
        assert len(objects) == 0

    def test_create_polyanet_direct(self):
        """Test direct Polyanet creation."""
        polyanet = self.factory.create_polyanet(1, 2)

        assert isinstance(polyanet, Polyanet)
        assert polyanet.position.row == 1
        assert polyanet.position.column == 2

    def test_create_soloon_direct(self):
        """Test direct Soloon creation."""
        soloon = self.factory.create_soloon(0, 1, "purple")

        assert isinstance(soloon, Soloon)
        assert soloon.position.row == 0
        assert soloon.position.column == 1
        assert soloon.color == "purple"

    def test_create_cometh_direct(self):
        """Test direct Cometh creation."""
        cometh = self.factory.create_cometh(2, 0, "down")

        assert isinstance(cometh, Cometh)
        assert cometh.position.row == 2
        assert cometh.position.column == 0
        assert cometh.direction == "down"

    def test_group_by_type(self):
        """Test grouping objects by type."""
        objects = [
            Polyanet(Position(0, 0)),
            Soloon(Position(1, 1), "blue"),
            Polyanet(Position(2, 2)),
            Cometh(Position(3, 3), "up"),
            Soloon(Position(4, 4), "red"),
        ]

        groups = self.factory.group_by_type(objects)

        assert len(groups) == 3
        assert len(groups["Polyanet"]) == 2
        assert len(groups["Soloon"]) == 2
        assert len(groups["Cometh"]) == 1

    def test_get_creation_order(self):
        """Test optimal creation order."""
        objects = [
            Cometh(Position(2, 2), "up"),
            Soloon(Position(1, 1), "blue"),
            Polyanet(Position(0, 0)),
            Polyanet(Position(3, 3)),
            Soloon(Position(4, 4), "red"),
        ]

        ordered = self.factory.get_creation_order(objects)

        # Should be ordered: Polyanets, then Soloons, then Comeths
        assert len(ordered) == 5
        assert isinstance(ordered[0], Polyanet)
        assert isinstance(ordered[1], Polyanet)
        assert isinstance(ordered[2], Soloon)
        assert isinstance(ordered[3], Soloon)
        assert isinstance(ordered[4], Cometh)

        # Within each type, should be sorted by position
        assert ordered[0].position.row == 0  # First Polyanet
        assert ordered[1].position.row == 3  # Second Polyanet

    def test_various_soloon_colors(self):
        """Test creating Soloons with various colors."""
        colors = ["RED", "BLUE", "PURPLE", "WHITE"]

        for color in colors:
            cell_value = f"{color}_SOLOON"
            obj = self.factory.create_from_cell(cell_value, 0, 0)

            assert isinstance(obj, Soloon)
            assert obj.color == color.lower()
            assert obj.get_object_type() == cell_value

    def test_various_cometh_directions(self):
        """Test creating Comeths with various directions."""
        directions = ["UP", "DOWN", "LEFT", "RIGHT"]

        for direction in directions:
            cell_value = f"{direction}_COMETH"
            obj = self.factory.create_from_cell(cell_value, 0, 0)

            assert isinstance(obj, Cometh)
            assert obj.direction == direction.lower()
            assert obj.get_object_type() == cell_value

    def test_create_from_map_with_errors(self):
        """Test creating from map with invalid cells."""
        goal_map = [["POLYANET", "INVALID_OBJECT"], ["BLUE_SOLOON", "SPACE"]]

        with pytest.raises(ObjectCreationError) as exc_info:
            self.factory.create_from_map(goal_map)

        assert "Unknown object type" in str(exc_info.value)
