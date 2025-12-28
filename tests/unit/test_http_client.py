"""Tests for HTTP client."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from vaulty.exceptions import (
    VaultyAPIError,
    VaultyAuthenticationError,
    VaultyAuthorizationError,
    VaultyNotFoundError,
    VaultyRateLimitError,
    VaultyValidationError,
)
from vaulty.http import HTTPClient


@pytest.mark.asyncio
async def test_http_client_init_with_api_token():
    """Test HTTPClient initialization with API token."""
    client = HTTPClient(base_url="https://api.test.com", api_token="test-token")
    assert client.base_url == "https://api.test.com"
    assert client.api_token == "test-token"
    assert client.auth_header == "Bearer test-token"
    assert client.api_version == "v1"
    await client.close()


@pytest.mark.asyncio
async def test_http_client_init_with_jwt_token():
    """Test HTTPClient initialization with JWT token."""
    client = HTTPClient(base_url="https://api.test.com", jwt_token="jwt-token")
    assert client.jwt_token == "jwt-token"
    assert client.auth_header == "Bearer jwt-token"
    await client.close()


@pytest.mark.asyncio
async def test_http_client_init_no_auth():
    """Test HTTPClient initialization without auth."""
    client = HTTPClient(base_url="https://api.test.com")
    assert client.api_token is None
    assert client.jwt_token is None
    assert client.auth_header is None
    await client.close()


@pytest.mark.asyncio
async def test_http_client_get_client():
    """Test HTTPClient._get_client creates client with correct headers."""
    client = HTTPClient(base_url="https://api.test.com", api_token="test-token")

    httpx_client = await client._get_client()
    assert httpx_client is not None
    assert httpx_client.base_url == "https://api.test.com"

    await client.close()


@pytest.mark.asyncio
async def test_http_client_close():
    """Test HTTPClient.close closes underlying client."""
    client = HTTPClient(base_url="https://api.test.com")
    await client._get_client()
    assert client._client is not None

    await client.close()
    assert client._client is None


@pytest.mark.asyncio
async def test_http_client_raise_for_status_success():
    """Test _raise_for_status doesn't raise on success."""
    client = HTTPClient(base_url="https://api.test.com")
    response = MagicMock()
    response.is_success = True
    response.status_code = 200

    # Should not raise
    client._raise_for_status(response)
    await client.close()


@pytest.mark.asyncio
async def test_http_client_raise_for_status_401():
    """Test _raise_for_status raises VaultyAuthenticationError on 401."""
    client = HTTPClient(base_url="https://api.test.com")
    response = MagicMock()
    response.is_success = False
    response.status_code = 401
    response.json.return_value = {"detail": "Invalid token"}
    response.text = ""

    with pytest.raises(VaultyAuthenticationError) as exc_info:
        client._raise_for_status(response)

    assert exc_info.value.status_code == 401
    await client.close()


@pytest.mark.asyncio
async def test_http_client_raise_for_status_403():
    """Test _raise_for_status raises VaultyAuthorizationError on 403."""
    client = HTTPClient(base_url="https://api.test.com")
    response = MagicMock()
    response.is_success = False
    response.status_code = 403
    response.json.return_value = {"detail": "Insufficient permissions"}
    response.text = ""

    with pytest.raises(VaultyAuthorizationError) as exc_info:
        client._raise_for_status(response)

    assert exc_info.value.status_code == 403
    await client.close()


@pytest.mark.asyncio
async def test_http_client_raise_for_status_404():
    """Test _raise_for_status raises VaultyNotFoundError on 404."""
    client = HTTPClient(base_url="https://api.test.com")
    response = MagicMock()
    response.is_success = False
    response.status_code = 404
    response.json.return_value = {"detail": "Not found"}
    response.text = ""

    with pytest.raises(VaultyNotFoundError) as exc_info:
        client._raise_for_status(response)

    assert exc_info.value.status_code == 404
    await client.close()


@pytest.mark.asyncio
async def test_http_client_raise_for_status_400():
    """Test _raise_for_status raises VaultyValidationError on 400."""
    client = HTTPClient(base_url="https://api.test.com")
    response = MagicMock()
    response.is_success = False
    response.status_code = 400
    response.json.return_value = {"detail": "Validation error"}
    response.text = ""

    with pytest.raises(VaultyValidationError) as exc_info:
        client._raise_for_status(response)

    assert exc_info.value.status_code == 400
    await client.close()


@pytest.mark.asyncio
async def test_http_client_raise_for_status_429():
    """Test _raise_for_status raises VaultyRateLimitError on 429."""
    client = HTTPClient(base_url="https://api.test.com")
    response = MagicMock()
    response.is_success = False
    response.status_code = 429
    response.json.return_value = {"detail": "Rate limit exceeded"}
    response.text = ""
    response.headers = {"Retry-After": "60"}

    with pytest.raises(VaultyRateLimitError) as exc_info:
        client._raise_for_status(response)

    assert exc_info.value.status_code == 429
    assert exc_info.value.retry_after == 60
    await client.close()


@pytest.mark.asyncio
async def test_http_client_raise_for_status_500():
    """Test _raise_for_status raises VaultyAPIError on 500."""
    client = HTTPClient(base_url="https://api.test.com")
    response = MagicMock()
    response.is_success = False
    response.status_code = 500
    response.json.return_value = {"detail": "Internal server error"}
    response.text = ""

    with pytest.raises(VaultyAPIError) as exc_info:
        client._raise_for_status(response)

    assert exc_info.value.status_code == 500
    await client.close()


@pytest.mark.asyncio
async def test_http_client_request():
    """Test HTTPClient.request makes request correctly."""
    client = HTTPClient(base_url="https://api.test.com", api_token="test-token")

    mock_response = MagicMock()
    mock_response.is_success = True
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": "test"}
    mock_response.text = ""

    with patch.object(client, "_get_client", return_value=AsyncMock()) as mock_get_client:
        mock_httpx_client = await mock_get_client()
        mock_httpx_client.request = AsyncMock(return_value=mock_response)

        response = await client.request("GET", "/test", params={"key": "value"})

        assert response == mock_response
        mock_httpx_client.request.assert_called_once()
        call_kwargs = mock_httpx_client.request.call_args[1]
        assert call_kwargs["method"] == "GET"
        assert call_kwargs["url"] == "/test"
        assert call_kwargs["params"] == {"key": "value"}

    await client.close()


@pytest.mark.asyncio
async def test_http_client_get():
    """Test HTTPClient.get."""
    client = HTTPClient(base_url="https://api.test.com")

    mock_response = MagicMock()
    mock_response.is_success = True
    mock_response.status_code = 200
    mock_response.json.return_value = {}
    mock_response.text = ""

    with patch.object(client, "request", return_value=mock_response) as mock_request:
        response = await client.get("/test", params={"key": "value"})

        assert response == mock_response
        mock_request.assert_called_once_with("GET", "/test", params={"key": "value"})

    await client.close()


@pytest.mark.asyncio
async def test_http_client_post():
    """Test HTTPClient.post."""
    client = HTTPClient(base_url="https://api.test.com")

    mock_response = MagicMock()
    mock_response.is_success = True
    mock_response.status_code = 200
    mock_response.json.return_value = {}
    mock_response.text = ""

    with patch.object(client, "request", return_value=mock_response) as mock_request:
        response = await client.post("/test", json={"key": "value"})

        assert response == mock_response
        mock_request.assert_called_once_with("POST", "/test", json={"key": "value"})

    await client.close()


@pytest.mark.asyncio
async def test_http_client_path_normalization():
    """Test HTTPClient normalizes paths."""
    client = HTTPClient(base_url="https://api.test.com")

    mock_response = MagicMock()
    mock_response.is_success = True
    mock_response.status_code = 200
    mock_response.json.return_value = {}
    mock_response.text = ""

    with patch.object(client, "_get_client", return_value=AsyncMock()) as mock_get_client:
        mock_httpx_client = await mock_get_client()
        mock_httpx_client.request = AsyncMock(return_value=mock_response)

        # Path without leading slash should be normalized
        await client.request("GET", "test")

        call_kwargs = mock_httpx_client.request.call_args[1]
        assert call_kwargs["url"] == "/test"

    await client.close()
