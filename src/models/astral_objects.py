from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class Position:
    """Represents a position in the megaverse grid."""

    row: int
    column: int


class AstralObject(ABC):
    """Abstract base class for all astral objects in the megaverse."""

    def __init__(self, position: Position):
        self.position = position

    @abstractmethod
    def get_api_endpoint(self) -> str:
        """Return the API endpoint for this object type."""
        pass

    @abstractmethod
    def get_payload(self, candidate_id: str) -> Dict[str, Any]:
        """Return the API payload for creating this object."""
        pass

    @abstractmethod
    def get_object_type(self) -> str:
        """Return the object type name."""
        pass

    def __str__(self) -> str:
        return f"{self.get_object_type()} at ({self.position.row}, {self.position.column})"


class Polyanet(AstralObject):
    """Represents a POLYanet object."""

    def get_api_endpoint(self) -> str:
        return "polyanets"

    def get_payload(self, candidate_id: str) -> Dict[str, Any]:
        return {
            "candidateId": candidate_id,
            "row": self.position.row,
            "column": self.position.column,
        }

    def get_object_type(self) -> str:
        return "POLYANET"


class Soloon(AstralObject):
    """Represents a SOLoon object with a color attribute."""

    def __init__(self, position: Position, color: str):
        super().__init__(position)
        self.color = color.lower()

    def get_api_endpoint(self) -> str:
        return "soloons"

    def get_payload(self, candidate_id: str) -> Dict[str, Any]:
        return {
            "candidateId": candidate_id,
            "row": self.position.row,
            "column": self.position.column,
            "color": self.color,
        }

    def get_object_type(self) -> str:
        return f"{self.color.upper()}_SOLOON"


class Cometh(AstralObject):
    """Represents a comETH object with a direction attribute."""

    def __init__(self, position: Position, direction: str):
        super().__init__(position)
        self.direction = direction.lower()

    def get_api_endpoint(self) -> str:
        return "comeths"

    def get_payload(self, candidate_id: str) -> Dict[str, Any]:
        return {
            "candidateId": candidate_id,
            "row": self.position.row,
            "column": self.position.column,
            "direction": self.direction,
        }

    def get_object_type(self) -> str:
        return f"{self.direction.upper()}_COMETH"
