/**
 * Integration tests for WAVE JavaScript client
 */

import { shouldSkipIntegrationTests, createTestClient } from '../test-config.js';

describe('WaveClient Integration Tests', () => {
    beforeAll(() => {
        if (shouldSkipIntegrationTests()) {
            console.log('Skipping integration tests - no API key provided in .env file');
        }
    });

    describe('API Connectivity', () => {
        test('should connect to real API when API key is provided', async () => {
            if (shouldSkipIntegrationTests()) {
                return; // Skip test
            }

            const client = await createTestClient();

            // Test health endpoint (doesn't require authentication)
            const health = await client.getHealth();
            expect(health).toHaveProperty('status');
            expect(health).toHaveProperty('service');
        });

        test('should get version information', async () => {
            if (shouldSkipIntegrationTests()) {
                return; // Skip test
            }

            const client = await createTestClient();

            const version = await client.getVersion();
            expect(version).toHaveProperty('api_version');
            expect(version).toHaveProperty('compatibility_rule');
        });
    });

    describe('Authentication Flow', () => {
        test('should handle authentication with valid API key', async () => {
            if (shouldSkipIntegrationTests()) {
                return; // Skip test
            }

            const client = await createTestClient();
            expect(client.apiKey).toBeTruthy();
        });
    });
});
