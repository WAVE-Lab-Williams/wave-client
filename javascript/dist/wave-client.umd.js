(function (global, factory) {
    typeof exports === 'object' && typeof module !== 'undefined' ? factory(exports) :
    typeof define === 'function' && define.amd ? define(['exports'], factory) :
    (global = typeof globalThis !== 'undefined' ? globalThis : global || self, factory(global.WaveClient = {}));
})(this, (function (exports) { 'use strict';

    /**
     * Error classes for the WAVE JavaScript client
     */

    class WaveClientError extends Error {
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

    /**
     * Create appropriate error from HTTP response
     * @param {Response} response - Fetch API response
     * @param {Object} errorData - Parsed error response body
     * @returns {WaveClientError} Appropriate error instance
     */
    function createErrorFromResponse(response, errorData) {
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

    /**
     * WAVE JavaScript Client
     *
     * Simple client for logging experiment data to the WAVE Backend API.
     * Focused on experiment data collection with robust error handling and retry logic.
     *
     * **Authentication**: Uses URL parameter-based API key extraction for browser security.
     * Add your API key to the URL: `?key=exp_abc123` or provide manually in constructor.
     *
     * **Security Benefits**:
     * - No API keys exposed in JavaScript source code or bundles
     * - Each experiment session gets unique temporary key via URL
     * - Prevents accidental exposure in version control
     *
     * @example
     * // Import using default export syntax
     * import WaveClient from 'https://cdn.jsdelivr.net/gh/WAVE-Lab-Williams/wave-client@v1.0.0/javascript/dist/wave-client.esm.js';
     *
     * // URL-based authentication (recommended)
     * // URL: https://experiment-site.com/task.html?key=exp_abc123&participant=P001
     * const client = new WaveClient();
     *
     * @example
     * // Manual API key (for testing or special cases)
     * const client = new WaveClient({ apiKey: "exp_abc123" });
     */


    class WaveClient {
        /**
         * Create a WAVE client instance
         * @param {Object} options - Configuration options
         * @param {string} [options.apiKey] - API key (overrides URL parameter extraction)
         * @param {string} [options.baseUrl='http://localhost:8000'] - Base URL for API
         * @param {number} [options.timeout=30000] - Request timeout in milliseconds (generous for experiments)
         * @param {number} [options.retries=5] - Maximum number of retries (prevent data loss)
         * @param {number} [options.baseDelay=1000] - Base delay for exponential backoff (ms)
         * @param {number} [options.maxDelay=30000] - Maximum delay between retries (ms)
         *
         * @example
         * // Automatic URL parameter extraction (recommended for browser experiments)
         * // URL: https://experiment-site.com/task.html?key=exp_abc123
         * const client = new WaveClient();
         *
         * @example
         * // Manual API key (overrides URL parameter)
         * const client = new WaveClient({
         *   apiKey: "exp_abc123",
         *   baseUrl: "https://api.example.com"
         * });
         */
        constructor(options = {}) {
            // Configuration
            this.apiKey = options.apiKey || this._getApiKeyFromUrl();
            this.baseUrl =
                options.baseUrl || this._getEnvVar('WAVE_API_URL') || 'http://localhost:8000';
            this.timeout = options.timeout || 30000;
            this.maxRetries = options.retries || 5;
            this.baseDelay = options.baseDelay || 1000;
            this.maxDelay = options.maxDelay || 30000;

            // Client version for compatibility checking
            this.clientVersion = '1.0.0';

            // Validate API key is present
            if (!this.apiKey) {
                throw new AuthenticationError(
                    'API key is required. Provide apiKey option or include "key" parameter in URL.'
                );
            }

            // Ensure baseUrl doesn't end with slash
            this.baseUrl = this.baseUrl.replace(/\/$/, '');
        }

        /**
         * Primary method: Log experiment data
         * @param {string} experimentId - Experiment UUID
         * @param {string} participantId - Participant identifier
         * @param {Object} data - Experiment data matching the experiment type schema
         * @returns {Promise<Object>} Created data row with all fields
         */
        async logExperimentData(experimentId, participantId, data) {
            if (!experimentId) {
                throw new ValidationError('experimentId is required');
            }
            if (!participantId) {
                throw new ValidationError('participantId is required');
            }
            if (!data || typeof data !== 'object' || Array.isArray(data)) {
                throw new ValidationError('data must be a non-empty object');
            }

            const requestBody = {
                participant_id: participantId,
                data: data,
            };

            const url = `/api/v1/experiment-data/${experimentId}/data/`;
            return await this._makeRequest('POST', url, requestBody);
        }

        /**
         * Get API health status
         * @returns {Promise<Object>} Health status
         */
        async getHealth() {
            return await this._makeRequest('GET', '/health');
        }

        /**
         * Get API version and compatibility information
         * @returns {Promise<Object>} Version information
         */
        async getVersion() {
            return await this._makeRequest('GET', '/version');
        }

        /**
         * Update base URL
         * @param {string} baseUrl - New base URL
         */
        setBaseUrl(baseUrl) {
            if (!baseUrl) {
                throw new ValidationError('Base URL cannot be empty');
            }
            this.baseUrl = baseUrl.replace(/\/$/, '');
        }

        /**
         * Make HTTP request with retry logic
         * @private
         * @param {string} method - HTTP method
         * @param {string} url - URL path (relative to baseUrl)
         * @param {Object} [body] - Request body for POST/PUT requests
         * @param {number} [attempt=1] - Current attempt number
         * @returns {Promise<Object>} Response data
         */
        async _makeRequest(method, url, body = null, attempt = 1) {
            const fullUrl = `${this.baseUrl}${url}`;

            const headers = {
                Authorization: `Bearer ${this.apiKey}`,
                'X-WAVE-Client-Version': this.clientVersion,
                'Content-Type': 'application/json',
            };

            const requestOptions = {
                method,
                headers,
            };

            // Add timeout support (AbortSignal.timeout is not available in older environments)
            if (typeof AbortSignal !== 'undefined' && AbortSignal.timeout) {
                requestOptions.signal = AbortSignal.timeout(this.timeout);
            } else if (typeof AbortController !== 'undefined') {
                // Fallback for older environments
                const controller = new AbortController();
                requestOptions.signal = controller.signal;
                setTimeout(() => controller.abort(), this.timeout);
            }

            if (body && (method === 'POST' || method === 'PUT')) {
                requestOptions.body = JSON.stringify(body);
            }

            try {
                const response = await fetch(fullUrl, requestOptions);

                if (!response.ok) {
                    // Parse error response
                    let errorData;
                    try {
                        errorData = await response.json();
                    } catch {
                        errorData = { detail: response.statusText };
                    }

                    const error = createErrorFromResponse(response, errorData);

                    // Retry logic for retryable errors
                    if (this._shouldRetry(error, attempt)) {
                        const delay = this._calculateDelay(attempt, error.retryAfter);
                        console.warn(
                            `Request failed (${error.name}), retrying in ${delay}ms (attempt ${attempt}/${this.maxRetries})`
                        );

                        await this._sleep(delay);
                        return await this._makeRequest(method, url, body, attempt + 1);
                    }

                    throw error;
                }

                // Parse successful response
                const responseData = await response.json();
                return responseData;
            } catch (error) {
                // Handle network errors and timeouts
                if (error.name === 'AbortError') {
                    const timeoutError = new WaveClientError(`Request timeout after ${this.timeout}ms`);

                    if (this._shouldRetry(timeoutError, attempt)) {
                        const delay = this._calculateDelay(attempt);
                        console.warn(
                            `Request timeout, retrying in ${delay}ms (attempt ${attempt}/${this.maxRetries})`
                        );

                        await this._sleep(delay);
                        return await this._makeRequest(method, url, body, attempt + 1);
                    }

                    throw timeoutError;
                }

                // Re-throw WAVE client errors
                if (error instanceof WaveClientError) {
                    throw error;
                }

                // Handle other network errors
                const networkError = new WaveClientError(`Network error: ${error.message}`);

                if (this._shouldRetry(networkError, attempt)) {
                    const delay = this._calculateDelay(attempt);
                    console.warn(
                        `Network error, retrying in ${delay}ms (attempt ${attempt}/${this.maxRetries})`
                    );

                    await this._sleep(delay);
                    return await this._makeRequest(method, url, body, attempt + 1);
                }

                throw networkError;
            }
        }

        /**
         * Determine if request should be retried
         * @private
         * @param {Error} error - Error that occurred
         * @param {number} attempt - Current attempt number
         * @returns {boolean} Whether to retry
         */
        _shouldRetry(error, attempt) {
            if (attempt > this.maxRetries) {
                return false;
            }

            // Don't retry client errors (4xx except rate limiting)
            if (
                error instanceof ValidationError ||
                error instanceof AuthenticationError ||
                error instanceof AuthorizationError ||
                error instanceof NotFoundError
            ) {
                return false;
            }

            // Retry rate limits and server errors
            if (
                error instanceof RateLimitError ||
                error instanceof ServerError ||
                error.name === 'AbortError' ||
                error instanceof WaveClientError
            ) {
                return true;
            }

            return false;
        }

        /**
         * Calculate delay for exponential backoff with jitter
         * @private
         * @param {number} attempt - Current attempt number
         * @param {number} [retryAfter] - Server-specified retry delay (ms)
         * @returns {number} Delay in milliseconds
         */
        _calculateDelay(attempt, retryAfter = null) {
            if (retryAfter) {
                // Honor server-specified delay for rate limiting
                return Math.min(retryAfter, this.maxDelay);
            }

            // Exponential backoff with jitter
            const exponentialDelay = this.baseDelay * Math.pow(2, attempt - 1);
            const jitter = Math.random() * 1000; // Add randomness to avoid thundering herd

            return Math.min(exponentialDelay + jitter, this.maxDelay);
        }

        /**
         * Sleep for specified duration
         * @private
         * @param {number} ms - Milliseconds to sleep
         * @returns {Promise<void>}
         */
        _sleep(ms) {
            return new Promise((resolve) => setTimeout(resolve, ms));
        }

        /**
         * Extract API key from URL parameters (browser-based authentication)
         * @private
         * @returns {string|null} API key from URL parameter or null if not found
         * @example
         * // URL: https://experiment-site.com/task.html?key=exp_abc123&participant=P001
         * // Returns: "exp_abc123"
         *
         * // URL: https://experiment-site.com/task.html#key=exp_def456
         * // Returns: "exp_def456"
         */
        _getApiKeyFromUrl() {
            // In Node.js test environment, check global references
            const windowObj = typeof window !== 'undefined' ? window : global.window;
            const URLSearchParamsClass =
                typeof URLSearchParams !== 'undefined' ? URLSearchParams : global.URLSearchParams;

            // Check if we're in a browser environment
            if (!windowObj || !URLSearchParamsClass) {
                return null; // Not in browser environment
            }

            try {
                // Check query parameters (?key=...)
                const urlParams = new URLSearchParamsClass(windowObj.location.search);
                const queryKey = urlParams.get('key');
                if (queryKey) return queryKey;

                // Check hash parameters (#key=...)
                const hashParams = new URLSearchParamsClass(windowObj.location.hash.substring(1));
                const hashKey = hashParams.get('key');
                if (hashKey) return hashKey;

                return null;
            } catch (error) {
                console.warn('Failed to extract API key from URL:', error.message);
                return null;
            }
        }

        /**
         * Get environment variable (Node.js only for security)
         * @private
         * @param {string} name - Environment variable name
         * @returns {string|undefined} Environment variable value
         */
        _getEnvVar(name) {
            // Node.js environment only
            if (typeof process !== 'undefined' && process.env) {
                return process.env[name];
            }

            // Browser environment: require explicit apiKey parameter
            // Environment variables in browser bundles are always public
            return undefined;
        }
    }

    exports.AuthenticationError = AuthenticationError;
    exports.AuthorizationError = AuthorizationError;
    exports.NotFoundError = NotFoundError;
    exports.RateLimitError = RateLimitError;
    exports.ServerError = ServerError;
    exports.ValidationError = ValidationError;
    exports.WaveClientError = WaveClientError;
    exports.default = WaveClient;

    Object.defineProperty(exports, '__esModule', { value: true });

}));
//# sourceMappingURL=wave-client.umd.js.map
