"""Custom exceptions for the megaverse application."""

from typing import Optional


class MegaverseError(Exception):
    """Base exception for megaverse operations."""

    pass


class APIError(MegaverseError):
    """API communication errors."""

    def __init__(
        self, message: str, status_code: Optional[int] = None, response_text: Optional[str] = None
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response_text = response_text

    def __str__(self) -> str:
        base_msg = super().__str__()
        if self.status_code:
            base_msg += f" (Status: {self.status_code})"
        if self.response_text:
            base_msg += f" - {self.response_text}"
        return base_msg


class ValidationError(MegaverseError):
    """Input validation errors."""

    pass


class ConfigurationError(MegaverseError):
    """Configuration errors."""

    pass


class GoalMapError(MegaverseError):
    """Goal map loading and parsing errors."""

    pass


class ObjectCreationError(MegaverseError):
    """Object creation and factory errors."""

    pass
