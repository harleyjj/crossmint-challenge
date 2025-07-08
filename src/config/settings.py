from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration settings for the megaverse application."""

    api_base_url: str = Field(default="https://challenge.crossmint.io/api")
    candidate_id: str = Field(..., description="Your Crossmint candidate ID")
    request_delay: float = Field(default=1.0, description="Delay between API requests in seconds")
    max_retries: int = Field(default=3, description="Maximum number of retry attempts")
    goal_file: str = Field(default="goal.json", description="Path to goal map file")
    log_level: str = Field(default="INFO", description="Logging level")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="forbid")


def get_settings() -> Settings:
    """Get application settings singleton."""
    # Check if we have a .env file first
    import os

    if os.path.exists(".env"):
        try:
            return Settings()
        except Exception:
            # If validation fails (e.g., missing CANDIDATE_ID), fall back to dummy
            return Settings(candidate_id="dummy_id_for_testing")
    # Otherwise, create settings with a dummy candidate_id
    return Settings(candidate_id="dummy_id_for_testing")
