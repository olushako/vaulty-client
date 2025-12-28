"""Tests for SecretResource client."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from vaulty.resources.secrets import SecretResource
from vaulty.http import HTTPClient
from vaulty.models import SecretResponse, SecretValueResponse, PaginatedResponse
from vaulty.retry import RetryConfig


@pytest.fixture
def http_client():
    """Create HTTPClient for testing."""
    return HTTPClient(base_url="https://api.test.com", api_token="test-token")


@pytest.fixture
def secret_resource(http_client):
    """Create SecretResource for testing."""
    return SecretResource(http_client)


@pytest.mark.asyncio
async def test_secret_resource_create(secret_resource, http_client):
    """Test SecretResource.create."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "id": "s-123",
        "project_id": "p-456",
        "key": "API_KEY",
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": "2025-01-01T00:00:00Z"
    }
    
    with patch.object(http_client, 'post', return_value=mock_response):
        result = await secret_resource.create("test-project", "API_KEY", "secret-value")
        
        assert isinstance(result, SecretResponse)
        assert result.key == "API_KEY"
        http_client.post.assert_called_once()
    
    await http_client.close()


@pytest.mark.asyncio
async def test_secret_resource_list(secret_resource, http_client):
    """Test SecretResource.list."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "items": [
            {
                "id": "s-123",
                "project_id": "p-456",
                "key": "API_KEY",
                "created_at": "2025-01-01T00:00:00Z",
                "updated_at": "2025-01-01T00:00:00Z"
            }
        ],
        "total": 1,
        "page": 1,
        "page_size": 50,
        "total_pages": 1,
        "has_next": False,
        "has_previous": False
    }
    
    with patch.object(http_client, 'get', return_value=mock_response):
        result = await secret_resource.list("test-project", page=1, page_size=50)
        
        assert isinstance(result, PaginatedResponse)
        assert len(result.items) == 1
        assert result.items[0].key == "API_KEY"
        http_client.get.assert_called_once()
    
    await http_client.close()


@pytest.mark.asyncio
async def test_secret_resource_get(secret_resource, http_client):
    """Test SecretResource.get."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "id": "s-123",
        "project_id": "p-456",
        "key": "API_KEY",
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": "2025-01-01T00:00:00Z"
    }
    
    with patch.object(http_client, 'get', return_value=mock_response):
        result = await secret_resource.get("test-project", "API_KEY")
        
        assert isinstance(result, SecretResponse)
        assert result.key == "API_KEY"
        http_client.get.assert_called_once()
    
    await http_client.close()


@pytest.mark.asyncio
async def test_secret_resource_get_value(secret_resource, http_client):
    """Test SecretResource.get_value."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "id": "s-123",
        "project_id": "p-456",
        "key": "API_KEY",
        "value": "decrypted-value",
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": "2025-01-01T00:00:00Z"
    }
    
    with patch.object(http_client, 'get', return_value=mock_response):
        result = await secret_resource.get_value("test-project", "API_KEY")
        
        assert isinstance(result, SecretValueResponse)
        assert result.value == "decrypted-value"
        http_client.get.assert_called_once()
    
    await http_client.close()


@pytest.mark.asyncio
async def test_secret_resource_update(secret_resource, http_client):
    """Test SecretResource.update."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "id": "s-123",
        "project_id": "p-456",
        "key": "API_KEY",
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": "2025-01-02T00:00:00Z"
    }
    
    with patch.object(http_client, 'patch', return_value=mock_response):
        result = await secret_resource.update("test-project", "API_KEY", "new-value")
        
        assert isinstance(result, SecretResponse)
        assert result.key == "API_KEY"
        http_client.patch.assert_called_once()
    
    await http_client.close()


@pytest.mark.asyncio
async def test_secret_resource_delete(secret_resource, http_client):
    """Test SecretResource.delete."""
    mock_response = MagicMock()
    mock_response.status_code = 204
    
    with patch.object(http_client, 'delete', return_value=mock_response):
        await secret_resource.delete("test-project", "API_KEY")
        
        http_client.delete.assert_called_once()
    
    await http_client.close()


@pytest.mark.asyncio
async def test_secret_resource_url_encoding(secret_resource, http_client):
    """Test SecretResource URL encodes project names."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "id": "s-123",
        "project_id": "p-456",
        "key": "API_KEY",
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": "2025-01-01T00:00:00Z"
    }
    
    with patch.object(http_client, 'get', return_value=mock_response) as mock_get:
        await secret_resource.get("test project", "API_KEY")
        
        # Check that URL was encoded
        call_args = mock_get.call_args
        assert "test%20project" in call_args[0][0] or "test+project" in call_args[0][0]
    
    await http_client.close()

