"""Exception classes for the WAVE Python client."""

from typing import Optional


class WaveClientError(Exception):
    """Base exception for all WAVE client errors."""

    def __init__(
        self, message: str, status_code: Optional[int] = None, detail: Optional[str] = None
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.detail = detail


class ValidationError(WaveClientError):
    """Raised when request data fails validation."""

    def __init__(self, message: str, detail: Optional[str] = None):
        super().__init__(message, 400, detail)


class AuthenticationError(WaveClientError):
    """Raised when API key is missing or invalid."""

    def __init__(self, message: str, detail: Optional[str] = None):
        super().__init__(message, 401, detail)


class AuthorizationError(WaveClientError):
    """Raised when API key doesn't have sufficient permissions."""

    def __init__(self, message: str, detail: Optional[str] = None):
        super().__init__(message, 403, detail)


class NotFoundError(WaveClientError):
    """Raised when requested resource doesn't exist."""

    def __init__(self, message: str, detail: Optional[str] = None):
        super().__init__(message, 404, detail)


class RateLimitError(WaveClientError):
    """Raised when request is rate limited."""

    def __init__(
        self, message: str, detail: Optional[str] = None, retry_after: Optional[float] = None
    ):
        super().__init__(message, 429, detail)
        self.retry_after = retry_after  # seconds to wait


class ServerError(WaveClientError):
    """Raised when server returns 5xx error."""

    def __init__(self, message: str, status_code: int, detail: Optional[str] = None):
        super().__init__(message, status_code, detail)
