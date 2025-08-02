/**
 * Shared test utilities for WAVE JavaScript client tests
 */

import WaveClient from '../src/wave-client.js';

/**
 * Common test setup and teardown utilities
 */
export class TestSetup {
    static setupGlobalMocks() {
        // Mock fetch globally for unit tests
        global.fetch = jest.fn();

        // Store original console.warn
        this.originalConsoleWarn = console.warn;
        console.warn = jest.fn();
    }

    static teardownGlobalMocks() {
        // Restore console.warn
        if (this.originalConsoleWarn) {
            console.warn = this.originalConsoleWarn;
        }
    }

    static createTestClient(overrides = {}) {
        return new WaveClient({
            apiKey: 'test-api-key',
            baseUrl: 'http://localhost:8000',
            timeout: 5000,
            retries: 2,
            baseDelay: 10, // Much faster retries for testing
            maxDelay: 50,
            ...overrides
        });
    }

    static clearMocks() {
        if (global.fetch && global.fetch.mockClear) {
            global.fetch.mockClear();
        }
        if (console.warn && console.warn.mockClear) {
            console.warn.mockClear();
        }
    }
}

/**
 * Browser environment mocking utilities
 */
export class BrowserMocks {
    static setupWindowMock(location = { search: '', hash: '' }) {
        this.originalWindow = global.window;
        global.window = { location };
        return this.originalWindow;
    }

    static setupURLSearchParamsMock(mockImplementation) {
        this.originalURLSearchParams = global.URLSearchParams;
        global.URLSearchParams = mockImplementation;
        return this.originalURLSearchParams;
    }

    static restoreWindowMock() {
        if (this.originalWindow !== undefined) {
            global.window = this.originalWindow;
        }
    }

    static restoreURLSearchParamsMock() {
        if (this.originalURLSearchParams !== undefined) {
            global.URLSearchParams = this.originalURLSearchParams;
        }
    }

    static restoreAll() {
        this.restoreWindowMock();
        this.restoreURLSearchParamsMock();
    }
}

/**
 * Common test helpers
 */
export const TestHelpers = {
    /**
     * Create a mock URLSearchParams implementation for testing
     */
    createURLSearchParamsMock(paramMap) {
        return jest.fn().mockImplementation(() => ({
            get: jest.fn((name) => paramMap[name] || null)
        }));
    },

    /**
     * Create a sequential URLSearchParams mock for testing hash fallback
     */
    createSequentialURLSearchParamsMock(queryParams, hashParams) {
        let callCount = 0;
        return jest.fn().mockImplementation(() => {
            callCount++;
            return {
                get: jest.fn((name) => {
                    if (callCount === 1) {
                        return queryParams[name] || null;
                    } else if (callCount === 2) {
                        return hashParams[name] || null;
                    }
                    return null;
                })
            };
        });
    }
};
