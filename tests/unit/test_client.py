"""Tests for VaultyClient."""

import pytest
import os
from unittest.mock import patch, MagicMock
from vaulty.client import VaultyClient
from vaulty.http import HTTPClient
from vaulty.auth import AuthHandler


@pytest.mark.asyncio
async def test_vaulty_client_init_with_api_token():
    """Test VaultyClient initialization with API token."""
    client = VaultyClient(
        base_url="https://api.test.com",
        api_token="test-token"
    )
    
    assert client.http_client.base_url == "https://api.test.com"
    assert client.http_client.api_token == "test-token"
    assert isinstance(client.auth, AuthHandler)
    assert client.customers is not None
    assert client.projects is not None
    assert client.secrets is not None
    assert client.tokens is not None
    assert client.activities is not None
    assert client.health is not None
    
    await client.close()


@pytest.mark.asyncio
async def test_vaulty_client_init_with_jwt_token():
    """Test VaultyClient initialization with JWT token."""
    client = VaultyClient(
        base_url="https://api.test.com",
        jwt_token="jwt-token"
    )
    
    assert client.http_client.jwt_token == "jwt-token"
    await client.close()


@pytest.mark.asyncio
async def test_vaulty_client_init_custom_config():
    """Test VaultyClient initialization with custom config."""
    client = VaultyClient(
        base_url="https://api.test.com",
        api_token="test-token",
        timeout=60.0,
        max_retries=5,
        retry_backoff_factor=3.0
    )
    
    assert client.http_client.timeout == 60.0
    assert client.retry_config.max_retries == 5
    assert client.retry_config.backoff_factor == 3.0
    
    await client.close()


@pytest.mark.asyncio
async def test_vaulty_client_from_env():
    """Test VaultyClient.from_env."""
    with patch.dict(os.environ, {"VAULTY_API_TOKEN": "env-token"}):
        client = VaultyClient.from_env()
        
        assert client.http_client.api_token == "env-token"
        await client.close()


@pytest.mark.asyncio
async def test_vaulty_client_from_env_jwt():
    """Test VaultyClient.from_env with JWT token."""
    with patch.dict(os.environ, {"VAULTY_JWT_TOKEN": "jwt-token"}, clear=True):
        client = VaultyClient.from_env()
        
        assert client.http_client.jwt_token == "jwt-token"
        await client.close()


def test_vaulty_client_from_env_no_token():
    """Test VaultyClient.from_env raises error when no token."""
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError, match="VAULTY_API_TOKEN or VAULTY_JWT_TOKEN"):
            VaultyClient.from_env()


@pytest.mark.asyncio
async def test_vaulty_client_from_config():
    """Test VaultyClient.from_config."""
    with patch.dict(os.environ, {"VAULTY_API_TOKEN": "config-token"}):
        client = VaultyClient.from_config()
        
        assert client.http_client.api_token == "config-token"
        await client.close()


def test_vaulty_client_from_config_no_token():
    """Test VaultyClient.from_config raises error when no token."""
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError, match="VAULTY_API_TOKEN"):
            VaultyClient.from_config()


@pytest.mark.asyncio
async def test_vaulty_client_context_manager():
    """Test VaultyClient as async context manager."""
    async with VaultyClient(base_url="https://api.test.com", api_token="test-token") as client:
        assert client.http_client is not None
    
    # Client should be closed after context exit
    assert client.http_client._client is None


@pytest.mark.asyncio
async def test_vaulty_client_close():
    """Test VaultyClient.close."""
    client = VaultyClient(base_url="https://api.test.com", api_token="test-token")
    
    # Initialize HTTP client
    await client.http_client._get_client()
    assert client.http_client._client is not None
    
    await client.close()
    assert client.http_client._client is None

