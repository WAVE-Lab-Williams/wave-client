/**
 * Error handling tests for WAVE JavaScript client
 */

import WaveClient, { WaveClientError, RateLimitError } from '../../src/wave-client.js';
import { MOCK_DATA, createMockFetch } from '../../test-config.js';
import { TestSetup } from '../test-utils.js';

describe('WaveClient Error Handling', () => {
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

    describe('Network Errors', () => {
        test('should handle network errors', async () => {
            fetch.mockImplementation(createMockFetch(null, { shouldReject: true }));

            await expect(client.logExperimentData(
                MOCK_DATA.experimentId,
                MOCK_DATA.participantId,
                MOCK_DATA.experimentData
            )).rejects.toThrow(WaveClientError);
        });

        test('should handle timeout errors', async () => {
            fetch.mockImplementation(() => {
                const error = new Error('Request timeout');
                error.name = 'AbortError';
                throw error;
            });

            await expect(client.logExperimentData(
                MOCK_DATA.experimentId,
                MOCK_DATA.participantId,
                MOCK_DATA.experimentData
            )).rejects.toThrow(WaveClientError);
        });
    });

    describe('Rate Limiting', () => {
        test('should parse Retry-After header correctly', async () => {
            const mockFetch = jest.fn().mockImplementation(async () => ({
                ok: false,
                status: 429,
                statusText: 'Too Many Requests',
                headers: {
                    get: (name) => name === 'Retry-After' ? '2' : null // 2 seconds
                },
                json: async () => MOCK_DATA.errorResponses.rateLimit
            }));

            fetch.mockImplementation(mockFetch);

            try {
                await client.logExperimentData(
                    MOCK_DATA.experimentId,
                    MOCK_DATA.participantId,
                    MOCK_DATA.experimentData
                );
            } catch (error) {
                expect(error).toBeInstanceOf(RateLimitError);
                expect(error.retryAfter).toBe(2000); // 2 seconds in milliseconds
            }
        }, 3000); // Shorter timeout since we're using fast retry settings

        test('should handle missing Retry-After header', async () => {
            const mockFetch = jest.fn().mockImplementation(async () => ({
                ok: false,
                status: 429,
                statusText: 'Too Many Requests',
                headers: {
                    get: () => null // No Retry-After header
                },
                json: async () => MOCK_DATA.errorResponses.rateLimit
            }));

            fetch.mockImplementation(mockFetch);

            try {
                await client.logExperimentData(
                    MOCK_DATA.experimentId,
                    MOCK_DATA.participantId,
                    MOCK_DATA.experimentData
                );
            } catch (error) {
                expect(error).toBeInstanceOf(RateLimitError);
                expect(error.retryAfter).toBeUndefined();
            }
        });
    });

    describe('Response Parsing', () => {
        test('should handle malformed JSON responses', async () => {
            fetch.mockImplementation(async () => ({
                ok: false,
                status: 500,
                statusText: 'Internal Server Error',
                headers: { get: () => null },
                json: async () => {
                    throw new Error('Invalid JSON');
                }
            }));

            await expect(client.logExperimentData(
                MOCK_DATA.experimentId,
                MOCK_DATA.participantId,
                MOCK_DATA.experimentData
            )).rejects.toThrow(WaveClientError);
        });

        test('should handle empty response bodies', async () => {
            fetch.mockImplementation(async () => ({
                ok: false,
                status: 500,
                statusText: 'Internal Server Error',
                headers: { get: () => null },
                json: async () => null
            }));

            await expect(client.logExperimentData(
                MOCK_DATA.experimentId,
                MOCK_DATA.participantId,
                MOCK_DATA.experimentData
            )).rejects.toThrow(WaveClientError);
        });
    });
});
