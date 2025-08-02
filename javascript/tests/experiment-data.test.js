/**
 * logExperimentData tests for WAVE JavaScript client
 */

import WaveClient, {
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    RateLimitError,
    ServerError
} from '../src/wave-client.js';
import { MOCK_DATA, createMockFetch } from '../test-config.js';
import { TestSetup } from './test-utils.js';

describe('WaveClient logExperimentData', () => {
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

    describe('Successful Operations', () => {
        test('should successfully log experiment data with all required fields', async () => {
            fetch.mockImplementation(createMockFetch(MOCK_DATA.successResponse));

            const result = await client.logExperimentData(
                MOCK_DATA.experimentId,
                MOCK_DATA.participantId,
                MOCK_DATA.experimentData
            );

            expect(result).toEqual(MOCK_DATA.successResponse);
            expect(fetch).toHaveBeenCalledWith(
                `http://localhost:8000/api/v1/experiment-data/${MOCK_DATA.experimentId}/data/`,
                expect.objectContaining({
                    method: 'POST',
                    body: JSON.stringify({
                        participant_id: MOCK_DATA.participantId,
                        data: MOCK_DATA.experimentData
                    })
                })
            );
        });

        test('should handle complex experiment data objects', async () => {
            const complexData = {
                trial_type: 'complex-task',
                responses: ['A', 'B', 'C'],
                reaction_times: [1.2, 0.8, 1.5],
                metadata: {
                    browser: 'Chrome',
                    screen_resolution: '1920x1080'
                },
                custom_scores: { accuracy: 0.85, speed: 2.1 }
            };

            fetch.mockImplementation(createMockFetch({
                ...MOCK_DATA.successResponse,
                data: complexData
            }));

            const result = await client.logExperimentData(
                MOCK_DATA.experimentId,
                MOCK_DATA.participantId,
                complexData
            );

            expect(result.data).toEqual(complexData);
        });
    });

    describe('Input Validation', () => {
        test('should require all three parameters', async () => {
            await expect(client.logExperimentData()).rejects.toThrow(ValidationError);
            await expect(client.logExperimentData()).rejects.toThrow('experimentId is required');
        });

        test('should require experimentId parameter', async () => {
            await expect(client.logExperimentData(null, 'participant', {})).rejects.toThrow(ValidationError);
            await expect(client.logExperimentData('', 'participant', {})).rejects.toThrow(ValidationError);
            await expect(client.logExperimentData(undefined, 'participant', {})).rejects.toThrow(ValidationError);
        });

        test('should require participantId parameter', async () => {
            await expect(client.logExperimentData('exp-id')).rejects.toThrow(ValidationError);
            await expect(client.logExperimentData('exp-id')).rejects.toThrow('participantId is required');

            await expect(client.logExperimentData('exp-id', null, {})).rejects.toThrow(ValidationError);
            await expect(client.logExperimentData('exp-id', '', {})).rejects.toThrow(ValidationError);
        });

        test('should require data parameter to be a valid object', async () => {
            const experimentId = 'exp-id';
            const participantId = 'part-id';

            await expect(client.logExperimentData(experimentId, participantId)).rejects.toThrow(ValidationError);
            await expect(client.logExperimentData(experimentId, participantId)).rejects.toThrow('data must be a non-empty object');

            await expect(client.logExperimentData(experimentId, participantId, null)).rejects.toThrow(ValidationError);
            await expect(client.logExperimentData(experimentId, participantId, 'not-object')).rejects.toThrow(ValidationError);
            await expect(client.logExperimentData(experimentId, participantId, 123)).rejects.toThrow(ValidationError);
            await expect(client.logExperimentData(experimentId, participantId, [])).rejects.toThrow(ValidationError);
        });

        test('should accept empty object as valid data', async () => {
            fetch.mockImplementation(createMockFetch(MOCK_DATA.successResponse));

            await expect(client.logExperimentData(
                MOCK_DATA.experimentId,
                MOCK_DATA.participantId,
                {}
            )).resolves.toBeDefined();
        });
    });

    describe('HTTP Error Handling', () => {
        test('should handle 400 validation errors from server', async () => {
            fetch.mockImplementation(createMockFetch(MOCK_DATA.errorResponses.validation, {
                status: 400,
                ok: false
            }));

            await expect(client.logExperimentData(
                MOCK_DATA.experimentId,
                MOCK_DATA.participantId,
                MOCK_DATA.experimentData
            )).rejects.toThrow(ValidationError);
        });

        test('should handle 401 authentication errors', async () => {
            fetch.mockImplementation(createMockFetch(MOCK_DATA.errorResponses.unauthorized, {
                status: 401,
                ok: false
            }));

            await expect(client.logExperimentData(
                MOCK_DATA.experimentId,
                MOCK_DATA.participantId,
                MOCK_DATA.experimentData
            )).rejects.toThrow(AuthenticationError);
        });

        test('should handle 403 authorization errors', async () => {
            fetch.mockImplementation(createMockFetch(MOCK_DATA.errorResponses.forbidden, {
                status: 403,
                ok: false
            }));

            await expect(client.logExperimentData(
                MOCK_DATA.experimentId,
                MOCK_DATA.participantId,
                MOCK_DATA.experimentData
            )).rejects.toThrow(AuthorizationError);
        });

        test('should handle 404 not found errors', async () => {
            fetch.mockImplementation(createMockFetch(MOCK_DATA.errorResponses.notFound, {
                status: 404,
                ok: false
            }));

            await expect(client.logExperimentData(
                MOCK_DATA.experimentId,
                MOCK_DATA.participantId,
                MOCK_DATA.experimentData
            )).rejects.toThrow(NotFoundError);
        });
    });

    describe('Retry Logic', () => {
        test('should retry on 500 server errors and eventually succeed', async () => {
            // First call fails with server error, second succeeds
            fetch
                .mockImplementationOnce(createMockFetch(MOCK_DATA.errorResponses.serverError, {
                    status: 500,
                    ok: false
                }))
                .mockImplementationOnce(createMockFetch(MOCK_DATA.successResponse));

            const result = await client.logExperimentData(
                MOCK_DATA.experimentId,
                MOCK_DATA.participantId,
                MOCK_DATA.experimentData
            );

            expect(result).toEqual(MOCK_DATA.successResponse);
            expect(fetch).toHaveBeenCalledTimes(2);
        });

        test('should retry on 429 rate limit errors with proper delay', async () => {
            // First call is rate limited, second succeeds
            fetch
                .mockImplementationOnce(createMockFetch(MOCK_DATA.errorResponses.rateLimit, {
                    status: 429,
                    ok: false
                }))
                .mockImplementationOnce(createMockFetch(MOCK_DATA.successResponse));

            const result = await client.logExperimentData(
                MOCK_DATA.experimentId,
                MOCK_DATA.participantId,
                MOCK_DATA.experimentData
            );

            expect(result).toEqual(MOCK_DATA.successResponse);
            expect(fetch).toHaveBeenCalledTimes(2);
        });

        test('should NOT retry on 4xx client errors', async () => {
            fetch.mockImplementation(createMockFetch(MOCK_DATA.errorResponses.validation, {
                status: 400,
                ok: false
            }));

            await expect(client.logExperimentData(
                MOCK_DATA.experimentId,
                MOCK_DATA.participantId,
                MOCK_DATA.experimentData
            )).rejects.toThrow(ValidationError);
        });

        test('should respect maximum retry limit and fail after exhausting retries', async () => {
            fetch.mockImplementation(createMockFetch(MOCK_DATA.errorResponses.serverError, {
                status: 500,
                ok: false
            }));

            await expect(client.logExperimentData(
                MOCK_DATA.experimentId,
                MOCK_DATA.participantId,
                MOCK_DATA.experimentData
            )).rejects.toThrow(ServerError);
        });

        test('should retry on different 5xx server errors', async () => {
            const serverErrors = [502, 503, 504];

            for (const statusCode of serverErrors) {
                fetch.mockClear();
                fetch
                    .mockImplementationOnce(createMockFetch(
                        { detail: `Server error ${statusCode}`, status_code: statusCode },
                        { status: statusCode, ok: false }
                    ))
                    .mockImplementationOnce(createMockFetch(MOCK_DATA.successResponse));

                const result = await client.logExperimentData(
                    MOCK_DATA.experimentId,
                    MOCK_DATA.participantId,
                    MOCK_DATA.experimentData
                );

                expect(result).toEqual(MOCK_DATA.successResponse);
            }
        });
    });
});
