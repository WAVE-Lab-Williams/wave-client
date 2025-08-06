/**
 * Utility method tests for WAVE JavaScript client
 */

import WaveClient, { ValidationError } from '../../src/wave-client.js';
import { MOCK_DATA, createMockFetch } from '../test-config.js';
import { TestSetup } from '../test-utils.js';

describe('WaveClient Utility Methods', () => {
    let client;

    beforeAll(() => {
        TestSetup.setupGlobalMocks();
    });

    afterAll(() => {
        TestSetup.teardownGlobalMocks();
    });

    beforeEach(() => {
        TestSetup.clearMocks();
        client = TestSetup.createTestClient();
    });

    describe('Health Check', () => {
        test('should return health status', async () => {
            fetch.mockImplementation(createMockFetch(MOCK_DATA.healthResponse));

            const result = await client.getHealth();
            expect(result).toEqual(MOCK_DATA.healthResponse);
        });
    });

    describe('Version Information', () => {
        test('should return version info', async () => {
            fetch.mockImplementation(createMockFetch(MOCK_DATA.versionResponse));

            const result = await client.getVersion();
            expect(result).toEqual(MOCK_DATA.versionResponse);
        });
    });

    describe('Base URL Management', () => {
        test('should update base URL', () => {
            client.setBaseUrl('https://new-api.com/');
            expect(client.baseUrl).toBe('https://new-api.com');
        });

        test('should validate base URL input', () => {
            expect(() => client.setBaseUrl('')).toThrow(ValidationError);
            expect(() => client.setBaseUrl(null)).toThrow(ValidationError);
        });

        test('should normalize base URL by removing trailing slash', () => {
            client.setBaseUrl('https://api.example.com/');
            expect(client.baseUrl).toBe('https://api.example.com');
        });

        test('should handle base URL without trailing slash', () => {
            client.setBaseUrl('https://api.example.com');
            expect(client.baseUrl).toBe('https://api.example.com');
        });
    });
});
