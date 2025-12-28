"""Tests for authentication handler."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from vaulty.auth import AuthHandler
from vaulty.http import HTTPClient


@pytest.mark.asyncio
async def test_auth_handler_init():
    """Test AuthHandler initialization."""
    http_client = HTTPClient(base_url="https://api.test.com")
    auth = AuthHandler(http_client)
    
    assert auth.http_client == http_client
    assert auth._jwt_token is None
    
    await http_client.close()


@pytest.mark.asyncio
async def test_auth_handler_login():
    """Test AuthHandler.login."""
    http_client = HTTPClient(base_url="https://api.test.com")
    auth = AuthHandler(http_client)
    
    mock_response = MagicMock()
    mock_response.json.return_value = {"access_token": "jwt-token-123"}
    mock_response.is_success = True
    mock_response.status_code = 200
    mock_response.text = ""
    
    with patch.object(http_client, 'post', return_value=mock_response) as mock_post, \
         patch.object(http_client, 'close', return_value=None) as mock_close:
        
        result = await auth.login("test@example.com", "password123")
        
        assert result == {"access_token": "jwt-token-123"}
        assert auth._jwt_token == "jwt-token-123"
        mock_post.assert_called_once_with(
            "/api/customers/login",
            json={"email": "test@example.com", "password": "password123"}
        )
    
    await http_client.close()


@pytest.mark.asyncio
async def test_auth_handler_jwt_token_property():
    """Test AuthHandler.jwt_token property."""
    http_client = HTTPClient(base_url="https://api.test.com")
    auth = AuthHandler(http_client)
    
    assert auth.jwt_token is None
    
    auth.jwt_token = "test-token"
    assert auth.jwt_token == "test-token"
    assert http_client.jwt_token == "test-token"
    assert http_client.auth_header == "Bearer test-token"
    
    await http_client.close()


@pytest.mark.asyncio
async def test_auth_handler_login_updates_http_client():
    """Test AuthHandler.login updates HTTP client with JWT token."""
    http_client = HTTPClient(base_url="https://api.test.com")
    auth = AuthHandler(http_client)
    
    mock_response = MagicMock()
    mock_response.json.return_value = {"access_token": "new-jwt-token"}
    mock_response.is_success = True
    mock_response.status_code = 200
    mock_response.text = ""
    
    with patch.object(http_client, 'post', return_value=mock_response), \
         patch.object(http_client, 'close', return_value=None):
        
        await auth.login("test@example.com", "password123")
        
        assert http_client.jwt_token == "new-jwt-token"
        assert http_client.auth_header == "Bearer new-jwt-token"
    
    await http_client.close()

