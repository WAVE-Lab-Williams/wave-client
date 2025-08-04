/**
 * Setup file for small/unit tests
 * Configure test environment for fast, isolated unit tests
 */

// Mock fetch for unit tests to avoid real HTTP requests
global.fetch = jest.fn();

// Reset mocks before each test
beforeEach(() => {
    jest.clearAllMocks();
    global.fetch.mockClear();
});

// Helper to mock successful fetch responses
global.mockFetchSuccess = (data, status = 200) => {
    global.fetch.mockResolvedValueOnce({
        ok: status >= 200 && status < 300,
        status,
        statusText: status === 200 ? 'OK' : 'Error',
        json: jest.fn().mockResolvedValue(data),
        text: jest.fn().mockResolvedValue(JSON.stringify(data))
    });
};

// Helper to mock fetch errors
global.mockFetchError = (error = new Error('Network error')) => {
    global.fetch.mockRejectedValueOnce(error);
};
