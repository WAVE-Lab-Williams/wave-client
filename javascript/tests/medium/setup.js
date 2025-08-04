/**
 * Setup file for medium/integration tests
 * Configure test environment for integration tests that may use real HTTP requests
 */

import dotenv from 'dotenv';

// Load environment variables for integration tests
dotenv.config();

// Longer timeout for integration tests
jest.setTimeout(30000);

// No fetch mocking for integration tests - use real HTTP requests
