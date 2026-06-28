/**
 * Experiment config tests for WAVE JavaScript client
 */

import WaveClient, { ValidationError, NotFoundError } from '../../src/wave-client.js';
import { MOCK_DATA, createMockFetch } from '../test-config.js';
import { TestSetup } from '../test-utils.js';

describe('WaveClient getExperimentConfig', () => {
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

    test('should GET the experiment config endpoint and return the payload', async () => {
        const payload = {
            experiment_uuid: MOCK_DATA.experimentId,
            config: { number_of_repetitions: 2 }
        };
        fetch.mockImplementation(createMockFetch(payload));

        const result = await client.getExperimentConfig(MOCK_DATA.experimentId);

        expect(result).toEqual(payload);
        expect(fetch).toHaveBeenCalledWith(
            `http://localhost:8000/api/v1/experiments/${MOCK_DATA.experimentId}/config`,
            expect.objectContaining({ method: 'GET' })
        );
    });

    test('should return an empty config object when none is set', async () => {
        const payload = { experiment_uuid: MOCK_DATA.experimentId, config: {} };
        fetch.mockImplementation(createMockFetch(payload));

        const result = await client.getExperimentConfig(MOCK_DATA.experimentId);
        expect(result.config).toEqual({});
    });

    test('should require an experimentId', async () => {
        await expect(client.getExperimentConfig()).rejects.toThrow(ValidationError);
        await expect(client.getExperimentConfig('')).rejects.toThrow('experimentId is required');
        await expect(client.getExperimentConfig(null)).rejects.toThrow(ValidationError);
    });

    test('should surface 404 for an unknown experiment', async () => {
        fetch.mockImplementation(
            createMockFetch(MOCK_DATA.errorResponses.notFound, { status: 404, ok: false })
        );
        await expect(client.getExperimentConfig(MOCK_DATA.experimentId)).rejects.toThrow(
            NotFoundError
        );
    });
});
