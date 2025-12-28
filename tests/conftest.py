"""Shared test fixtures."""

from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from vaulty.auth import AuthHandler
from vaulty.http import HTTPClient


@pytest.fixture()
def mock_httpx_response():
    """Create a mock httpx.Response."""

    def _create(
        status_code: int = 200,
        json_data: dict | None = None,
        text: str | None = None,
        headers: dict | None = None,
    ):
        response = MagicMock(spec=httpx.Response)
        response.status_code = status_code
        response.is_success = 200 <= status_code < 300
        response.headers = headers or {}

        if json_data:
            response.json = MagicMock(return_value=json_data)
            response.text = ""
        elif text:
            response.text = text
            response.json = MagicMock(side_effect=ValueError("Not JSON"))
        else:
            response.json = MagicMock(return_value={})
            response.text = ""

        return response

    return _create


@pytest.fixture()
def mock_httpx_client():
    """Create a mock httpx.AsyncClient."""
    return AsyncMock(spec=httpx.AsyncClient)


@pytest.fixture()
def http_client():
    """Create HTTPClient instance for testing."""
    return HTTPClient(base_url="https://api.test.com", api_token="test-token")


@pytest.fixture()
def auth_handler(http_client):
    """Create AuthHandler instance for testing."""
    return AuthHandler(http_client)
