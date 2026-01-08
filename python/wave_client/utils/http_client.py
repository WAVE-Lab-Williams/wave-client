"""HTTP client with authentication and retry logic for WAVE API."""

import asyncio
import logging
import random
from typing import Any, Dict, Optional

import httpx
from wave_client.exceptions import (
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
    WaveClientError,
)
from wave_client.utils.versioning import get_client_version, log_version_info

logger = logging.getLogger(__name__)


class HTTPClient:
    """Async HTTP client with authentication and retry logic."""

    def __init__(
        self,
        api_key: str,
        base_url: str,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 30.0,
        timeout: float = 30.0,
    ):
        """Initialize HTTP client.

        Args:
            api_key: API key for authentication.
            base_url: Base URL for API.
            max_retries: Maximum number of retries for failed requests.
            base_delay: Base delay in seconds for exponential backoff.
            max_delay: Maximum delay in seconds between retries.
            timeout: Request timeout in seconds.
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.timeout = timeout

        # HTTP client will be created when needed
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        """Async context manager entry."""
        await self._ensure_client()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def _ensure_client(self):
        """Ensure HTTP client is created."""
        if self._client is None:
            client_version = get_client_version()
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "X-WAVE-Client-Version": client_version,
            }

            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers=headers,
                timeout=self.timeout,
            )

            # Log client version on first connection
            log_version_info(client_version)

    async def close(self):
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def request(  # noqa: C901
        self,
        method: str,
        url: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        attempt: int = 1,
    ) -> Dict[str, Any]:
        """Make HTTP request with retry logic.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE).
            url: URL path (relative to base_url).
            json_data: JSON data for request body.
            params: Query parameters.
            attempt: Current attempt number (for internal recursion).

        Returns:
            Response data as dictionary.

        Raises:
            WaveClientError: For various API errors.
        """
        await self._ensure_client()

        try:
            # Make the HTTP request
            response = await self._client.request(
                method=method,
                url=url,
                json=json_data,
                params=params,
            )

            # Handle server API version compatibility
            if "X-WAVE-API-Version" in response.headers:
                api_version = response.headers["X-WAVE-API-Version"]
                client_version = get_client_version()
                log_version_info(client_version, api_version)

            # Handle successful responses
            if response.status_code < 400:
                if response.headers.get("content-type", "").startswith("application/json"):
                    return response.json()
                else:
                    return {"message": response.text}

            # Handle error responses
            error_data = {}
            if response.headers.get("content-type", "").startswith("application/json"):
                try:
                    error_data = response.json()
                except Exception:
                    pass

            # Create appropriate error
            error = self._create_http_error(response.status_code, error_data, response)

            # Check if we should retry
            if self._should_retry(error, attempt):
                delay = self._calculate_delay(attempt, getattr(error, "retry_after", None))
                logger.warning(
                    f"Request failed with {error.status_code}, retrying in {delay:.1f}s "
                    f"(attempt {attempt}/{self.max_retries})"
                )
                await asyncio.sleep(delay)
                return await self.request(method, url, json_data, params, attempt + 1)

            raise error

        except Exception as e:
            if isinstance(e, WaveClientError):
                raise

            # Handle network errors
            if self._should_retry_network_error(e, attempt):
                delay = self._calculate_delay(attempt)
                logger.warning(
                    f"Network error, retrying in {delay:.1f}s "
                    f"(attempt {attempt}/{self.max_retries}): {e}"
                )
                await asyncio.sleep(delay)
                return await self.request(method, url, json_data, params, attempt + 1)

            raise WaveClientError(f"Request failed: {str(e)}")

    def _should_retry(self, error: WaveClientError, attempt: int) -> bool:
        """Determine if request should be retried."""
        if attempt >= self.max_retries:
            return False

        # Retry on rate limits and server errors
        if hasattr(error, "status_code"):
            retryable_codes = [429, 500, 502, 503, 504]
            return error.status_code in retryable_codes

        return False

    def _should_retry_network_error(self, error: Exception, attempt: int) -> bool:
        """Determine if network error should be retried."""
        if attempt >= self.max_retries:
            return False

        # Retry on timeout and connection errors
        return isinstance(error, (asyncio.TimeoutError, httpx.ConnectError, httpx.TimeoutException))

    def _calculate_delay(self, attempt: int, retry_after: Optional[float] = None) -> float:
        """Calculate delay before retry with exponential backoff."""
        if retry_after:
            return min(retry_after, self.max_delay)

        # Exponential backoff with jitter
        exponential_delay = self.base_delay * (2 ** (attempt - 1))
        jitter = random.uniform(0, 1)
        return min(exponential_delay + jitter, self.max_delay)

    def _create_http_error(
        self, status_code: int, error_data: Dict[str, Any], response: httpx.Response
    ) -> WaveClientError:
        """Convert HTTP error to appropriate client error."""
        message = error_data.get("message", f"HTTP {status_code} error")
        detail = error_data.get("detail", response.text)

        if status_code == 400:
            return ValidationError(message, detail)
        elif status_code == 401:
            return AuthenticationError(message, detail)
        elif status_code == 403:
            return AuthorizationError(message, detail)
        elif status_code == 404:
            return NotFoundError(message, detail)
        elif status_code == 429:
            # Extract retry-after header if present
            retry_after = None
            if "Retry-After" in response.headers:
                try:
                    retry_after = float(response.headers["Retry-After"])
                except ValueError:
                    retry_after = 5.0
            return RateLimitError(message, detail, retry_after)
        elif status_code >= 500:
            return ServerError(message, status_code, detail)
        else:
            return WaveClientError(message, status_code, detail)
