"""Shared test fixtures."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from typing import Optional
import httpx
from vaulty.http import HTTPClient
from vaulty.auth import AuthHandler


@pytest.fixture
def mock_httpx_response():
    """Create a mock httpx.Response."""
    def _create(status_code: int = 200, json_data: dict = None, text: str = None, headers: dict = None):
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


@pytest.fixture
def mock_httpx_client():
    """Create a mock httpx.AsyncClient."""
    client = AsyncMock(spec=httpx.AsyncClient)
    return client


@pytest.fixture
def http_client():
    """Create HTTPClient instance for testing."""
    return HTTPClient(
        base_url="https://api.test.com",
        api_token="test-token"
    )


@pytest.fixture
def auth_handler(http_client):
    """Create AuthHandler instance for testing."""
    return AuthHandler(http_client)

