/**
 * Error classes for the WAVE JavaScript client
 */

export class WaveClientError extends Error {
    constructor(message, statusCode = null, detail = null, retryAfter = undefined) {
        super(message);
        this.name = 'WaveClientError';
        this.statusCode = statusCode;
        this.detail = detail;
        if (retryAfter !== undefined) {
            this.retryAfter = retryAfter; // milliseconds to wait before retry
        }
    }
}

export class ValidationError extends WaveClientError {
    constructor(message, detail) {
        super(message, 400, detail);
        this.name = 'ValidationError';
    }
}

export class AuthenticationError extends WaveClientError {
    constructor(message, detail) {
        super(message, 401, detail);
        this.name = 'AuthenticationError';
    }
}

export class AuthorizationError extends WaveClientError {
    constructor(message, detail) {
        super(message, 403, detail);
        this.name = 'AuthorizationError';
    }
}

export class NotFoundError extends WaveClientError {
    constructor(message, detail) {
        super(message, 404, detail);
        this.name = 'NotFoundError';
    }
}

export class RateLimitError extends WaveClientError {
    constructor(message, detail, retryAfter) {
        super(message, 429, detail, retryAfter);
        this.name = 'RateLimitError';
    }
}

export class ServerError extends WaveClientError {
    constructor(message, statusCode, detail) {
        super(message, statusCode, detail);
        this.name = 'ServerError';
    }
}

/**
 * Create appropriate error from HTTP response
 * @param {Response} response - Fetch API response
 * @param {Object} errorData - Parsed error response body
 * @returns {WaveClientError} Appropriate error instance
 */
export function createErrorFromResponse(response, errorData) {
    const { status } = response;
    const message = errorData?.detail || response.statusText || 'Unknown error';
    const detail = errorData?.detail;

    switch (status) {
        case 400:
            return new ValidationError(message, detail);
        case 401:
            return new AuthenticationError(message, detail);
        case 403:
            return new AuthorizationError(message, detail);
        case 404:
            return new NotFoundError(message, detail);
        case 429: {
            const retryAfter = parseRetryAfter(response.headers.get('Retry-After'));
            return new RateLimitError(message, detail, retryAfter);
        }
        case 500:
        case 502:
        case 503:
        case 504:
            return new ServerError(message, status, detail);
        default:
            return new WaveClientError(message, status, detail);
    }
}

/**
 * Parse Retry-After header value to milliseconds
 * @param {string|null} retryAfterHeader - Retry-After header value
 * @returns {number} Retry delay in milliseconds
 */
function parseRetryAfter(retryAfterHeader) {
    if (!retryAfterHeader) {
        return undefined; // Return undefined when no header is provided
    }

    // Handle both seconds (number) and HTTP date formats
    const seconds = parseInt(retryAfterHeader, 10);
    if (!isNaN(seconds)) {
        return seconds * 1000; // Convert to milliseconds
    }

    // Handle HTTP date format (less common for rate limiting)
    const date = new Date(retryAfterHeader);
    if (!isNaN(date.getTime())) {
        return Math.max(0, date.getTime() - Date.now());
    }

    return 5000; // Default fallback for invalid headers
}
