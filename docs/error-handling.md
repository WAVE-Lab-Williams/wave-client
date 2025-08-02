# Error Handling Strategy

This document defines the error handling approach for both JavaScript and Python WAVE clients, including error classes, retry logic, and recovery strategies.

## HTTP Status Code Mapping

Based on the backend API patterns, here are the standard error responses:

| Status Code | Meaning | Common Causes | Client Action |
|-------------|---------|---------------|---------------|
| 400 | Bad Request | Validation errors, missing fields, invalid data types | Show error, don't retry |
| 401 | Unauthorized | Missing/invalid API key | Check authentication, don't retry |
| 403 | Forbidden | Insufficient role permissions | Check role requirements, don't retry |
| 404 | Not Found | Resource doesn't exist | Check resource IDs, don't retry |
| 429 | Too Many Requests | Rate limiting (Unkey) | Retry with backoff |
| 500 | Internal Server Error | Server issues | Retry with backoff |
| 502/503/504 | Server Unavailable | Server down/overloaded | Retry with backoff |

## JavaScript Client Error Handling

### Error Classes

```javascript
class WaveClientError extends Error {
  constructor(message, statusCode = null, detail = null, retryAfter = null) {
    super(message);
    this.name = 'WaveClientError';
    this.statusCode = statusCode;
    this.detail = detail;
    this.retryAfter = retryAfter; // milliseconds to wait before retry
  }
}

class ValidationError extends WaveClientError {
  constructor(message, detail) {
    super(message, 400, detail);
    this.name = 'ValidationError';
  }
}

class AuthenticationError extends WaveClientError {
  constructor(message, detail) {
    super(message, 401, detail);
    this.name = 'AuthenticationError';
  }
}

class AuthorizationError extends WaveClientError {
  constructor(message, detail) {
    super(message, 403, detail);
    this.name = 'AuthorizationError';
  }
}

class NotFoundError extends WaveClientError {
  constructor(message, detail) {
    super(message, 404, detail);
    this.name = 'NotFoundError';
  }
}

class RateLimitError extends WaveClientError {
  constructor(message, detail, retryAfter) {
    super(message, 429, detail, retryAfter);
    this.name = 'RateLimitError';
  }
}

class ServerError extends WaveClientError {
  constructor(message, statusCode, detail) {
    super(message, statusCode, detail);
    this.name = 'ServerError';
  }
}
```

### Retry Logic

```javascript
class WaveClient {
  constructor(options = {}) {
    this.maxRetries = options.retries || 5;
    this.baseDelay = options.baseDelay || 1000; // 1 second
    this.maxDelay = options.maxDelay || 30000;  // 30 seconds
    this.timeout = options.timeout || 30000;    // 30 seconds - generous for experiments
  }

  async _makeRequest(method, url, data = null, attempt = 1) {
    try {
      const response = await this._httpRequest(method, url, data);
      return response;
    } catch (error) {
      if (this._shouldRetry(error, attempt)) {
        const delay = this._calculateDelay(attempt, error.retryAfter);
        console.warn(`Request failed, retrying in ${delay}ms (attempt ${attempt}/${this.maxRetries})`);
        await this._sleep(delay);
        return this._makeRequest(method, url, data, attempt + 1);
      }
      throw this._createError(error);
    }
  }

  _shouldRetry(error, attempt) {
    if (attempt >= this.maxRetries) return false;
    
    // Retry on rate limits and server errors
    const retryableStatusCodes = [429, 500, 502, 503, 504];
    return retryableStatusCodes.includes(error.statusCode);
  }

  _calculateDelay(attempt, retryAfter = null) {
    if (retryAfter) {
      // Server specified retry delay (rate limiting)
      return Math.min(retryAfter, this.maxDelay);
    }
    
    // Exponential backoff with jitter
    const exponentialDelay = this.baseDelay * Math.pow(2, attempt - 1);
    const jitter = Math.random() * 1000; // Add randomness
    return Math.min(exponentialDelay + jitter, this.maxDelay);
  }

  _createError(httpError) {
    const { statusCode, message, detail } = httpError;
    
    switch (statusCode) {
      case 400:
        return new ValidationError(message, detail);
      case 401:
        return new AuthenticationError(message, detail);
      case 403:
        return new AuthorizationError(message, detail);
      case 404:
        return new NotFoundError(message, detail);
      case 429:
        const retryAfter = httpError.retryAfter || 5000;
        return new RateLimitError(message, detail, retryAfter);
      case 500:
      case 502:
      case 503:
      case 504:
        return new ServerError(message, statusCode, detail);
      default:
        return new WaveClientError(message, statusCode, detail);
    }
  }
}
```

### URL Parameter Authentication Errors

The JavaScript client extracts API keys from URL parameters, which can lead to specific error scenarios:

#### Common URL Authentication Issues

```javascript
// 1. Missing API key in URL
// URL: https://experiment-site.com/task.html (no key parameter)
// Error: AuthenticationError: "API key is required. Provide apiKey option or include 'key' parameter in URL."

// 2. Empty API key parameter
// URL: https://experiment-site.com/task.html?key=
// Error: AuthenticationError: "API key cannot be empty"

// 3. Invalid API key format
// URL: https://experiment-site.com/task.html?key=invalid-key
// HTTP 401 response -> AuthenticationError: "Authentication failed: Invalid API key"

// 4. Wrong role permissions
// URL: https://experiment-site.com/task.html?key=admin_key_instead_of_exp_key
// HTTP 403 response -> AuthorizationError: "Authorization failed: Insufficient permissions. Required: EXPERIMENTEE, Found: ADMIN"
```

#### URL Parameter Extraction

```javascript
// Client automatically extracts from these URL formats:
// ?key=exp_abc123          - query parameter (most common)
// #key=exp_abc123          - hash parameter (alternative)
// ?key=exp_abc123&other=1  - with other parameters

// Manual override (for testing or special cases)
const client = new WaveClient({ 
  apiKey: "exp_abc123"  // overrides URL parameter extraction
});
```

### Usage Examples

```javascript
// Basic error handling with URL authentication
try {
  const result = await client.logExperimentData(experimentId, participantId, data);
  console.log('Data logged successfully:', result);
} catch (error) {
  if (error instanceof ValidationError) {
    console.error('Data validation failed:', error.detail);
    // Show user-friendly error message
  } else if (error instanceof AuthenticationError) {
    console.error('Authentication failed:', error.detail);
    // Check URL has valid key parameter: ?key=exp_abc123
    // Or provide explicit apiKey in constructor
  } else if (error instanceof RateLimitError) {
    console.warn('Rate limited, will retry automatically');
    // Client already retried, this shouldn't happen often
  } else {
    console.error('Unexpected error:', error.message);
    // Log for debugging, show generic error to user
  }
}

// Experiment-specific error handling (critical for data preservation)
async function safeLogExperimentData(client, experimentId, participantId, data) {
  const maxAttempts = 10; // More attempts for critical experiment data
  let lastError;
  
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      return await client.logExperimentData(experimentId, participantId, data);
    } catch (error) {
      lastError = error;
      
      if (error instanceof ValidationError || 
          error instanceof AuthenticationError || 
          error instanceof AuthorizationError ||
          error instanceof NotFoundError) {
        // Don't retry these errors
        throw error;
      }
      
      if (attempt === maxAttempts) {
        // Last attempt failed
        break;
      }
      
      // Wait longer between attempts for critical data
      const delay = Math.min(2000 * attempt, 30000);
      console.warn(`Data logging failed (attempt ${attempt}), retrying in ${delay}ms`);
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }
  
  // All attempts failed - store data locally for later sync
  console.error('Failed to log experiment data after all attempts:', lastError);
  storeDataForLaterSync(experimentId, participantId, data);
  throw lastError;
}
```

## Python Client Error Handling

### Error Classes

```python
"""Exception classes for the WAVE Python client."""

class WaveClientError(Exception):
    """Base exception for all WAVE client errors."""
    
    def __init__(self, message: str, status_code: int = None, detail: str = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.detail = detail

class ValidationError(WaveClientError):
    """Raised when request data fails validation."""
    
    def __init__(self, message: str, detail: str = None):
        super().__init__(message, 400, detail)

class AuthenticationError(WaveClientError):
    """Raised when API key is missing or invalid."""
    
    def __init__(self, message: str, detail: str = None):
        super().__init__(message, 401, detail)

class AuthorizationError(WaveClientError):
    """Raised when API key doesn't have sufficient permissions."""
    
    def __init__(self, message: str, detail: str = None):
        super().__init__(message, 403, detail)

class NotFoundError(WaveClientError):
    """Raised when requested resource doesn't exist."""
    
    def __init__(self, message: str, detail: str = None):
        super().__init__(message, 404, detail)

class RateLimitError(WaveClientError):
    """Raised when request is rate limited."""
    
    def __init__(self, message: str, detail: str = None, retry_after: float = None):
        super().__init__(message, 429, detail)
        self.retry_after = retry_after  # seconds to wait

class ServerError(WaveClientError):
    """Raised when server returns 5xx error."""
    
    def __init__(self, message: str, status_code: int, detail: str = None):
        super().__init__(message, status_code, detail)
```

### Retry Logic with Async Support

```python
import asyncio
import random
from typing import Any, Dict, Optional

class WaveClient:
    def __init__(self, api_key: str = None, base_url: str = None, 
                 max_retries: int = 3, base_delay: float = 1.0, 
                 max_delay: float = 30.0, timeout: float = 30.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.timeout = timeout

    async def _make_request(self, method: str, url: str, 
                           json_data: Dict[str, Any] = None, 
                           attempt: int = 1) -> Dict[str, Any]:
        """Make HTTP request with retry logic."""
        try:
            response = await self._http_request(method, url, json_data)
            return response
        except Exception as error:
            if self._should_retry(error, attempt):
                delay = self._calculate_delay(attempt, getattr(error, 'retry_after', None))
                logger.warning(f"Request failed, retrying in {delay:.1f}s (attempt {attempt}/{self.max_retries})")
                await asyncio.sleep(delay)
                return await self._make_request(method, url, json_data, attempt + 1)
            raise self._create_error(error)

    def _should_retry(self, error: Exception, attempt: int) -> bool:
        """Determine if request should be retried."""
        if attempt >= self.max_retries:
            return False
        
        # Retry on rate limits and server errors
        if hasattr(error, 'status_code'):
            retryable_codes = [429, 500, 502, 503, 504]
            return error.status_code in retryable_codes
        
        # Retry on network errors
        return isinstance(error, (asyncio.TimeoutError, ConnectionError))

    def _calculate_delay(self, attempt: int, retry_after: Optional[float] = None) -> float:
        """Calculate delay before retry with exponential backoff."""
        if retry_after:
            return min(retry_after, self.max_delay)
        
        # Exponential backoff with jitter
        exponential_delay = self.base_delay * (2 ** (attempt - 1))
        jitter = random.uniform(0, 1)
        return min(exponential_delay + jitter, self.max_delay)

    def _create_error(self, http_error: Exception) -> WaveClientError:
        """Convert HTTP error to appropriate client error."""
        if not hasattr(http_error, 'status_code'):
            return WaveClientError(str(http_error))
        
        status_code = http_error.status_code
        message = getattr(http_error, 'message', str(http_error))
        detail = getattr(http_error, 'detail', None)
        
        if status_code == 400:
            return ValidationError(message, detail)
        elif status_code == 401:
            return AuthenticationError(message, detail)
        elif status_code == 403:
            return AuthorizationError(message, detail)
        elif status_code == 404:
            return NotFoundError(message, detail)
        elif status_code == 429:
            retry_after = getattr(http_error, 'retry_after', 5.0)
            return RateLimitError(message, detail, retry_after)
        elif status_code >= 500:
            return ServerError(message, status_code, detail)
        else:
            return WaveClientError(message, status_code, detail)
```

### Usage Examples

```python
import asyncio
from wave_client import WaveClient
from wave_client.exceptions import (
    ValidationError, AuthenticationError, RateLimitError, 
    NotFoundError, ServerError
)

# Basic error handling
async def log_experiment_data():
    async with WaveClient() as client:
        try:
            result = await client.experiment_data.create(
                experiment_id, 
                {"participant_id": "PART-001", "data": {"score": 95}}
            )
            print(f"Data logged: {result['id']}")
        except ValidationError as e:
            print(f"Validation error: {e.detail}")
        except AuthenticationError as e:
            print(f"Authentication failed: {e.detail}")
        except NotFoundError as e:
            print(f"Experiment not found: {e.detail}")
        except RateLimitError as e:
            print(f"Rate limited, retry after {e.retry_after}s")
        except ServerError as e:
            print(f"Server error {e.status_code}: {e.detail}")

# Advanced error handling with custom retry logic
async def robust_data_collection():
    async with WaveClient(max_retries=5) as client:
        participants = ["PART-001", "PART-002", "PART-003"]
        results = []
        
        for participant in participants:
            max_attempts = 3
            for attempt in range(max_attempts):
                try:
                    result = await client.experiment_data.create(
                        experiment_id,
                        {
                            "participant_id": participant,
                            "data": generate_experiment_data()
                        }
                    )
                    results.append(result)
                    break  # Success, move to next participant
                    
                except (ValidationError, AuthenticationError, NotFoundError):
                    # Don't retry these errors
                    print(f"Permanent error for {participant}")
                    break
                    
                except (RateLimitError, ServerError) as e:
                    if attempt == max_attempts - 1:
                        print(f"Failed to log data for {participant} after {max_attempts} attempts")
                    else:
                        delay = 2 ** attempt  # Exponential backoff
                        print(f"Retrying {participant} in {delay}s...")
                        await asyncio.sleep(delay)
        
        return results

# Batch operations with error handling
async def batch_data_upload():
    async with WaveClient() as client:
        data_rows = [
            {"participant_id": f"PART-{i:03d}", "data": {"score": i * 10}}
            for i in range(1, 101)
        ]
        
        successful = []
        failed = []
        
        # Process in chunks to avoid overwhelming server
        chunk_size = 10
        for i in range(0, len(data_rows), chunk_size):
            chunk = data_rows[i:i + chunk_size]
            
            # Process chunk concurrently but with rate limiting
            semaphore = asyncio.Semaphore(3)  # Max 3 concurrent requests
            
            async def upload_row(row):
                async with semaphore:
                    try:
                        result = await client.experiment_data.create(experiment_id, row)
                        successful.append(result)
                    except Exception as e:
                        failed.append({"row": row, "error": str(e)})
            
            await asyncio.gather(*[upload_row(row) for row in chunk])
            
            # Small delay between chunks
            await asyncio.sleep(0.1)
        
        print(f"Upload complete: {len(successful)} successful, {len(failed)} failed")
        return successful, failed
```

## Error Recovery Strategies

### JavaScript Client (Experiment Focus)
- **Data Preservation**: Store failed uploads locally for later sync
- **User Feedback**: Clear, non-technical error messages during experiments
- **Graceful Degradation**: Continue experiment even if some data fails to upload
- **Background Sync**: Retry failed uploads when network conditions improve

### Python Client (Analysis Focus)
- **Data Consistency**: Ensure partial failures don't corrupt datasets
- **Batch Recovery**: Resume interrupted batch operations
- **Pandas Integration**: Handle errors during DataFrame conversions gracefully
- **Research Continuity**: Provide alternative data sources when primary fails

### Common Patterns
- **Rate Limit Respect**: Honor server-specified retry delays
- **Circuit Breaker**: Stop retrying after consecutive failures
- **Logging**: Comprehensive error logging for debugging
- **Monitoring**: Track error rates and patterns for system health

This error handling strategy ensures both clients can handle the challenges of real-world research environments while preserving critical experimental data.