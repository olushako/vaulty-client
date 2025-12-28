"""Tests for CLI utilities."""

import pytest
import os
from unittest.mock import patch, MagicMock, AsyncMock

# Skip CLI tests if CLI dependencies not available
try:
    from vaulty.cli.utils import get_client, get_project_from_token_scope, run_async, detect_cicd
    from vaulty.client import VaultyClient
    CLI_AVAILABLE = True
except ImportError:
    CLI_AVAILABLE = False


@pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI dependencies not available")
def test_get_client_from_env():
    """Test get_client loads from environment variables."""
    with patch.dict(os.environ, {
        "VAULTY_API_TOKEN": "env-token",
        "VAULTY_API_URL": "https://api.test.com"
    }):
        client = get_client()
        
        assert isinstance(client, VaultyClient)
        assert client.http_client.api_token == "env-token"
        assert client.http_client.base_url == "https://api.test.com"


@pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI dependencies not available")
def test_get_client_from_parameter():
    """Test get_client uses provided parameters."""
    client = get_client(token="param-token", base_url="https://param.test.com")
    
    assert isinstance(client, VaultyClient)
    assert client.http_client.api_token == "param-token"
    assert client.http_client.base_url == "https://param.test.com"


@pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI dependencies not available")
def test_get_client_no_token():
    """Test get_client raises error when no token."""
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError, match="No authentication token"):
            get_client()


@pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI dependencies not available")
@pytest.mark.asyncio
async def test_get_project_from_token_scope_single_project():
    """Test get_project_from_token_scope returns project info for project-scoped token."""
    client = MagicMock()
    
    mock_token = MagicMock()
    mock_token.scope = "project:p-12345:read/write"
    
    mock_result = MagicMock()
    mock_result.items = [mock_token]
    
    client.tokens = MagicMock()
    client.tokens.list = AsyncMock(return_value=mock_result)
    
    project_info = await get_project_from_token_scope(client)
    
    assert project_info is not None
    assert project_info["id"] == "p-12345"
    assert project_info["name"] == "p-12345"
    client.tokens.list.assert_called_once_with(page=1, page_size=1)


@pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI dependencies not available")
@pytest.mark.asyncio
async def test_get_project_from_token_scope_multiple_projects():
    """Test get_project_from_token_scope returns None for full-scope token."""
    client = MagicMock()
    
    mock_result = MagicMock()
    mock_result.total = 2
    mock_result.items = [MagicMock(), MagicMock()]
    
    client.projects = MagicMock()
    client.projects.list = AsyncMock(return_value=mock_result)
    
    project_name = await get_project_from_token_scope(client)
    
    assert project_name is None


@pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI dependencies not available")
@pytest.mark.asyncio
async def test_get_project_from_token_scope_no_projects():
    """Test get_project_from_token_scope returns None when no projects."""
    client = MagicMock()
    
    mock_result = MagicMock()
    mock_result.total = 0
    mock_result.items = []
    
    client.projects = MagicMock()
    client.projects.list = AsyncMock(return_value=mock_result)
    
    project_name = await get_project_from_token_scope(client)
    
    assert project_name is None


@pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI dependencies not available")
@pytest.mark.asyncio
async def test_get_project_from_token_scope_exception():
    """Test get_project_from_token_scope handles exceptions."""
    client = MagicMock()
    client.projects = MagicMock()
    client.projects.list = AsyncMock(side_effect=Exception("API error"))
    
    project_name = await get_project_from_token_scope(client)
    
    assert project_name is None


@pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI dependencies not available")
def test_run_async():
    """Test run_async runs async coroutine."""
    async def test_coro():
        return "result"
    
    result = run_async(test_coro())
    assert result == "result"


@pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI dependencies not available")
def test_detect_cicd_true():
    """Test detect_cicd returns True in CI/CD environment."""
    with patch.dict(os.environ, {"CI": "true"}):
        assert detect_cicd() is True


@pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI dependencies not available")
def test_detect_cicd_false():
    """Test detect_cicd returns False in non-CI/CD environment."""
    with patch.dict(os.environ, {}, clear=True):
        assert detect_cicd() is False


@pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI dependencies not available")
def test_detect_cicd_github_actions():
    """Test detect_cicd detects GitHub Actions."""
    with patch.dict(os.environ, {"GITHUB_ACTIONS": "true"}):
        assert detect_cicd() is True


@pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI dependencies not available")
def test_detect_cicd_gitlab_ci():
    """Test detect_cicd detects GitLab CI."""
    with patch.dict(os.environ, {"GITLAB_CI": "true"}):
        assert detect_cicd() is True

