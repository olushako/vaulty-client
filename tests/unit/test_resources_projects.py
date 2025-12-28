"""Tests for ProjectResource client."""

from unittest.mock import MagicMock, patch

import pytest

from vaulty.http import HTTPClient
from vaulty.models import PaginatedResponse, ProjectResponse
from vaulty.resources.projects import ProjectResource


@pytest.fixture()
def http_client():
    """Create HTTPClient for testing."""
    return HTTPClient(base_url="https://api.test.com", api_token="test-token")


@pytest.fixture()
def project_resource(http_client):
    """Create ProjectResource for testing."""
    return ProjectResource(http_client)


@pytest.mark.asyncio()
async def test_project_resource_create(project_resource, http_client):
    """Test ProjectResource.create."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "id": "p-123",
        "customer_id": "c-456",
        "name": "test-project",
        "description": "Test description",
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": "2025-01-01T00:00:00Z",
    }

    with patch.object(http_client, "post", return_value=mock_response):
        result = await project_resource.create("test-project", "Test description")

        assert isinstance(result, ProjectResponse)
        assert result.name == "test-project"
        http_client.post.assert_called_once()

    await http_client.close()


@pytest.mark.asyncio()
async def test_project_resource_list(project_resource, http_client):
    """Test ProjectResource.list."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "items": [
            {
                "id": "p-123",
                "customer_id": "c-456",
                "name": "test-project",
                "description": "Test",
                "created_at": "2025-01-01T00:00:00Z",
                "updated_at": "2025-01-01T00:00:00Z",
            }
        ],
        "total": 1,
        "page": 1,
        "page_size": 50,
        "total_pages": 1,
        "has_next": False,
        "has_previous": False,
    }

    with patch.object(http_client, "get", return_value=mock_response):
        result = await project_resource.list(page=1, page_size=50)

        assert isinstance(result, PaginatedResponse)
        assert len(result.items) == 1
        assert result.items[0].name == "test-project"
        http_client.get.assert_called_once()

    await http_client.close()


@pytest.mark.asyncio()
async def test_project_resource_get(project_resource, http_client):
    """Test ProjectResource.get."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "id": "p-123",
        "customer_id": "c-456",
        "name": "test-project",
        "description": "Test",
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": "2025-01-01T00:00:00Z",
    }

    with patch.object(http_client, "get", return_value=mock_response):
        result = await project_resource.get("test-project")

        assert isinstance(result, ProjectResponse)
        assert result.name == "test-project"
        http_client.get.assert_called_once()

    await http_client.close()


@pytest.mark.asyncio()
async def test_project_resource_update(project_resource, http_client):
    """Test ProjectResource.update."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "id": "p-123",
        "customer_id": "c-456",
        "name": "test-project",
        "description": "Updated description",
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": "2025-01-02T00:00:00Z",
    }

    with patch.object(http_client, "patch", return_value=mock_response):
        result = await project_resource.update("test-project", "Updated description")

        assert isinstance(result, ProjectResponse)
        assert result.description == "Updated description"
        http_client.patch.assert_called_once()

    await http_client.close()


@pytest.mark.asyncio()
async def test_project_resource_delete(project_resource, http_client):
    """Test ProjectResource.delete."""
    mock_response = MagicMock()
    mock_response.status_code = 204

    with patch.object(http_client, "delete", return_value=mock_response):
        await project_resource.delete("test-project")

        http_client.delete.assert_called_once()

    await http_client.close()
