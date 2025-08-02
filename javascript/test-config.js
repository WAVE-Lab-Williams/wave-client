/**
 * Test configuration for WAVE JavaScript client
 * 
 * This file handles test configuration and mocking for both unit and integration tests.
 * For integration tests, set WAVE_API_KEY and WAVE_API_URL in .env file.
 */

// For Node.js testing environment, try to load dotenv
let dotenv;
try {
  dotenv = require('dotenv');
  dotenv.config();
} catch (error) {
  // dotenv not available, that's fine for browser environments
}

export const TEST_CONFIG = {
  // API configuration for integration tests
  apiKey: process.env.WAVE_API_KEY,
  baseUrl: process.env.WAVE_API_URL || 'http://localhost:8000',
  
  // Test timeouts (shorter for tests)
  timeout: 5000,
  
  // Skip integration tests if no API key is provided
  skipIntegration: !process.env.WAVE_API_KEY
};

/**
 * Mock data for testing
 */
export const MOCK_DATA = {
  // Mock experiment UUID
  experimentId: '550e8400-e29b-41d4-a716-446655440000',
  
  // Mock participant ID
  participantId: 'TEST-PARTICIPANT-001',
  
  // Mock experiment data
  experimentData: {
    reaction_time: 1.234,
    accuracy: 0.85,
    difficulty_level: 2,
    stimulus_type: 'visual'
  },
  
  // Mock jsPsych trial data
  jsPsychTrialData: {
    rt: 1234,           // Reaction time in milliseconds
    response: 'correct',
    correct: true,
    stimulus: 'target_image.png',
    trial_type: 'image-keyboard-response',
    trial_index: 0,
    time_elapsed: 5432,
    internal_node_id: '0.0-0.0'
  },
  
  // Mock API responses
  successResponse: {
    id: 1,
    experiment_uuid: '550e8400-e29b-41d4-a716-446655440000',
    participant_id: 'TEST-PARTICIPANT-001',
    created_at: '2024-01-15T10:30:00Z',
    updated_at: '2024-01-15T10:30:00Z',
    reaction_time: 1.234,
    accuracy: 0.85,
    difficulty_level: 2,
    stimulus_type: 'visual'
  },
  
  healthResponse: {
    status: 'healthy',
    service: 'wave-backend'
  },
  
  versionResponse: {
    api_version: '1.0.0',
    client_version: '1.0.0',
    compatible: true,
    compatibility_rule: 'Semantic versioning: same major version = compatible'
  },
  
  // Mock error responses
  errorResponses: {
    validation: {
      detail: 'Validation error: participant_id is required',
      status_code: 400
    },
    unauthorized: {
      detail: 'Authentication failed: Invalid API key',
      status_code: 401
    },
    forbidden: {
      detail: 'Authorization failed: Insufficient permissions. Required: EXPERIMENTEE, Found: NONE',
      status_code: 403
    },
    notFound: {
      detail: 'Experiment not found',
      status_code: 404
    },
    rateLimit: {
      detail: 'Too many requests',
      status_code: 429
    },
    serverError: {
      detail: 'Internal server error',
      status_code: 500
    }
  }
};

/**
 * Check if integration tests should be skipped
 * @returns {boolean} True if integration tests should be skipped
 */
export function shouldSkipIntegrationTests() {
  return TEST_CONFIG.skipIntegration;
}

/**
 * Create a test client with test configuration
 * @returns {Promise<WaveClient>} Configured test client
 */
export async function createTestClient() {
  if (shouldSkipIntegrationTests()) {
    throw new Error('Integration tests are skipped - no API key provided in .env file');
  }
  
  const { default: WaveClient } = await import('./src/wave-client.js');
  
  return new WaveClient({
    apiKey: TEST_CONFIG.apiKey,
    baseUrl: TEST_CONFIG.baseUrl,
    timeout: TEST_CONFIG.timeout
  });
}

/**
 * Create a mock fetch function for unit tests
 * @param {Object} mockResponse - Mock response object
 * @param {Object} options - Mock options
 * @returns {Function} Mock fetch function
 */
export function createMockFetch(mockResponse, options = {}) {
  const {
    status = 200,
    ok = status < 400,
    delay = 0,
    shouldReject = false
  } = options;

  return jest.fn().mockImplementation(async (url, requestOptions) => {
    if (delay > 0) {
      await new Promise(resolve => setTimeout(resolve, delay));
    }

    if (shouldReject) {
      throw new Error('Network error');
    }

    return {
      ok,
      status,
      statusText: status === 200 ? 'OK' : 'Error',
      headers: {
        get: (name) => {
          if (name === 'Retry-After' && status === 429) {
            return '5'; // 5 seconds
          }
          return null;
        }
      },
      json: async () => mockResponse
    };
  });
}