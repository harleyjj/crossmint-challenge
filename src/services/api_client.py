"""API client for interacting with the Crossmint megaverse API."""

import logging
from typing import Any, Dict, Optional

import requests

from src.models.astral_objects import AstralObject
from src.models.exceptions import APIError
from src.utils.retry import retry_with_backoff


class APIClient:
    """Client for interacting with the Crossmint API."""

    def __init__(self, base_url: str, max_retries: int = 3):
        """
        Initialize the API client.

        Args:
            base_url: Base URL for the API
            max_retries: Maximum number of retry attempts
        """
        self.base_url = base_url.rstrip("/")
        self.max_retries = max_retries
        self.session = requests.Session()
        self.logger = logging.getLogger(__name__)

        # Set default headers
        self.session.headers.update(
            {"Content-Type": "application/json", "User-Agent": "Crossmint-Challenge-Client/1.0"}
        )

    @retry_with_backoff(max_retries=3, exceptions=(requests.exceptions.RequestException,))
    def create_object(self, astral_object: AstralObject, candidate_id: str) -> bool:
        """
        Create an astral object via the API.

        Args:
            astral_object: The astral object to create
            candidate_id: The candidate ID for API authentication

        Returns:
            True if successful, False otherwise

        Raises:
            APIError: If the API request fails
        """
        url = f"{self.base_url}/{astral_object.get_api_endpoint()}"
        payload = astral_object.get_payload(candidate_id)

        self.logger.debug(
            f"Creating {astral_object.get_object_type()} at {url} with payload: {payload}"
        )

        try:
            response = self.session.post(url, json=payload)

            if response.status_code == 200:
                self.logger.info(f"Successfully created {astral_object}")
                return True
            else:
                error_msg = f"Failed to create {astral_object}"
                self.logger.error(f"{error_msg}: {response.status_code} - {response.text}")
                raise APIError(error_msg, response.status_code, response.text)

        except requests.exceptions.RequestException as e:
            error_msg = f"Network error creating {astral_object}: {e}"
            self.logger.error(error_msg)
            raise APIError(error_msg)

    @retry_with_backoff(max_retries=3, exceptions=(requests.exceptions.RequestException,))
    def delete_object(self, astral_object: AstralObject, candidate_id: str) -> bool:
        """
        Delete an astral object via the API.

        Args:
            astral_object: The astral object to delete
            candidate_id: The candidate ID for API authentication

        Returns:
            True if successful, False otherwise

        Raises:
            APIError: If the API request fails
        """
        url = f"{self.base_url}/{astral_object.get_api_endpoint()}"
        payload = astral_object.get_payload(candidate_id)

        self.logger.debug(
            f"Deleting {astral_object.get_object_type()} at {url} with payload: {payload}"
        )

        try:
            response = self.session.delete(url, json=payload)

            if response.status_code == 200:
                self.logger.info(f"Successfully deleted {astral_object}")
                return True
            else:
                error_msg = f"Failed to delete {astral_object}"
                self.logger.error(f"{error_msg}: {response.status_code} - {response.text}")
                raise APIError(error_msg, response.status_code, response.text)

        except requests.exceptions.RequestException as e:
            error_msg = f"Network error deleting {astral_object}: {e}"
            self.logger.error(error_msg)
            raise APIError(error_msg)

    def get_current_map(self, candidate_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the current map state from the API.

        Args:
            candidate_id: The candidate ID for API authentication

        Returns:
            The current map data, or None if not available

        Raises:
            APIError: If the API request fails
        """
        url = f"{self.base_url}/map/{candidate_id}"

        try:
            response = self.session.get(url)

            if response.status_code == 200:
                return response.json()  # type: ignore[no-any-return]
            else:
                error_msg = "Failed to get current map"
                self.logger.error(f"{error_msg}: {response.status_code} - {response.text}")
                raise APIError(error_msg, response.status_code, response.text)

        except requests.exceptions.RequestException as e:
            error_msg = f"Network error getting current map: {e}"
            self.logger.error(error_msg)
            raise APIError(error_msg)

    def get_goal_map(self, candidate_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the goal map from the API.

        Args:
            candidate_id: The candidate ID for API authentication

        Returns:
            The goal map data, or None if not available

        Raises:
            APIError: If the API request fails
        """
        url = f"{self.base_url}/map/{candidate_id}/goal"

        try:
            response = self.session.get(url)

            if response.status_code == 200:
                return response.json()  # type: ignore[no-any-return]
            else:
                error_msg = "Failed to get goal map"
                self.logger.error(f"{error_msg}: {response.status_code} - {response.text}")
                raise APIError(error_msg, response.status_code, response.text)

        except requests.exceptions.RequestException as e:
            error_msg = f"Network error getting goal map: {e}"
            self.logger.error(error_msg)
            raise APIError(error_msg)

    def close(self) -> None:
        """Close the session."""
        self.session.close()
