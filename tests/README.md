# SDK Tests

Comprehensive test suite for the Vaulty Python SDK and CLI.

## Test Structure

```
tests/
├── unit/              # Unit tests (fast, isolated)
│   ├── test_exceptions.py
│   ├── test_http_client.py
│   ├── test_auth.py
│   ├── test_retry.py
│   ├── test_client.py
│   ├── test_resources_secrets.py
│   ├── test_resources_projects.py
│   └── test_cli_utils.py
├── integration/       # Integration tests (mocked API)
│   └── test_cli_commands.py
└── conftest.py        # Shared fixtures
```

## Running Tests

### Run All Tests

```bash
cd sdk
pytest tests/
```

### Run Unit Tests Only

```bash
pytest tests/unit/
```

### Run Integration Tests Only

```bash
pytest tests/integration/
```

### Run Specific Test File

```bash
pytest tests/unit/test_http_client.py
```

### Run with Coverage

```bash
pytest tests/ --cov=vaulty --cov-report=html
```

### Run in Parallel

```bash
pytest tests/ -n auto
```

## Test Coverage

### Core Components

- ✅ **Exceptions** (`test_exceptions.py`): All exception types
- ✅ **HTTP Client** (`test_http_client.py`): Request/response handling, error mapping
- ✅ **Auth Handler** (`test_auth.py`): Login, JWT token management
- ✅ **Retry Logic** (`test_retry.py`): Exponential backoff, rate limit handling
- ✅ **Main Client** (`test_client.py`): Client initialization, factory methods

### Resource Clients

- ✅ **Secrets** (`test_resources_secrets.py`): CRUD operations, URL encoding
- ✅ **Projects** (`test_resources_projects.py`): CRUD operations

### CLI Utilities

- ✅ **CLI Utils** (`test_cli_utils.py`): Client creation, project inference, CI/CD detection
- ⏭️ **CLI Commands** (`test_cli_commands.py`): Command execution (requires CLI dependencies)

## Test Requirements

### Core Dependencies

- `pytest>=7.4.0`
- `pytest-asyncio>=0.21.0`
- `pytest-cov>=4.1.0` (optional, for coverage)

### CLI Tests

CLI tests require optional dependencies:
- `click>=8.1.0`
- `pyyaml>=6.0`
- `rich>=13.0.0`
- `cryptography>=41.0.0`

Install CLI dependencies:
```bash
pip install -e ".[cli]"
```

## Test Patterns

### Async Tests

All async tests use `@pytest.mark.asyncio`:

```python
@pytest.mark.asyncio
async def test_async_function():
    result = await some_async_function()
    assert result == expected
```

### Mocking

Tests use `unittest.mock` for mocking:

```python
from unittest.mock import AsyncMock, MagicMock, patch

with patch.object(client, 'method', return_value=mock_response):
    result = await client.method()
    assert result == expected
```

### Fixtures

Shared fixtures in `conftest.py`:

- `mock_httpx_response`: Create mock HTTP responses
- `http_client`: HTTPClient instance
- `auth_handler`: AuthHandler instance

## Skipped Tests

Some tests are skipped if optional dependencies are not available:

- CLI utility tests (if `click` not installed)
- CLI command tests (if CLI dependencies not installed)

These tests will show as "skipped" in test output.

## Continuous Integration

Tests are designed to run in CI/CD environments:

- All tests are isolated (no shared state)
- Tests use UUIDs for unique data
- Tests can run in parallel
- No external dependencies required (mocked)

## Test Results

Current status: **73 passed, 5 skipped**

All core SDK functionality is tested and verified.

