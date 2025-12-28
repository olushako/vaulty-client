"""Tests for Vaulty exceptions."""

import pytest
from vaulty.exceptions import (
    VaultyError,
    VaultyAPIError,
    VaultyAuthenticationError,
    VaultyAuthorizationError,
    VaultyNotFoundError,
    VaultyValidationError,
    VaultyRateLimitError,
)


def test_vaulty_error():
    """Test base VaultyError."""
    error = VaultyError("Test error")
    assert str(error) == "Test error"
    assert isinstance(error, Exception)


def test_vaulty_api_error():
    """Test VaultyAPIError."""
    error = VaultyAPIError("API error", 500, "Internal server error")
    assert str(error) == "API error"
    assert error.status_code == 500
    assert error.detail == "Internal server error"
    assert isinstance(error, VaultyError)


def test_vaulty_authentication_error():
    """Test VaultyAuthenticationError."""
    error = VaultyAuthenticationError("Auth failed", 401, "Invalid token")
    assert str(error) == "Auth failed"
    assert error.status_code == 401
    assert isinstance(error, VaultyAPIError)


def test_vaulty_authorization_error():
    """Test VaultyAuthorizationError."""
    error = VaultyAuthorizationError("Forbidden", 403, "Insufficient permissions")
    assert str(error) == "Forbidden"
    assert error.status_code == 403
    assert isinstance(error, VaultyAPIError)


def test_vaulty_not_found_error():
    """Test VaultyNotFoundError."""
    error = VaultyNotFoundError("Not found", 404, "Resource not found")
    assert str(error) == "Not found"
    assert error.status_code == 404
    assert isinstance(error, VaultyAPIError)


def test_vaulty_validation_error():
    """Test VaultyValidationError."""
    error = VaultyValidationError("Validation failed", 400, "Invalid input")
    assert str(error) == "Validation failed"
    assert error.status_code == 400
    assert isinstance(error, VaultyAPIError)


def test_vaulty_rate_limit_error():
    """Test VaultyRateLimitError."""
    error = VaultyRateLimitError("Rate limit", 429, "Too many requests", retry_after=60)
    assert str(error) == "Rate limit"
    assert error.status_code == 429
    assert error.retry_after == 60
    assert isinstance(error, VaultyAPIError)


def test_vaulty_rate_limit_error_no_retry_after():
    """Test VaultyRateLimitError without retry_after."""
    error = VaultyRateLimitError("Rate limit", 429, "Too many requests")
    assert error.retry_after is None

