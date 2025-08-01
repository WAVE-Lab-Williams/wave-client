/**
 * Basic tests for WaveClient
 */

import { WaveClient } from './wave-client.js';

describe('WaveClient', () => {
    test('basic assertion', () => {
        expect(true).toBe(true);
    });

    test('can be instantiated', () => {
        const client = new WaveClient();
        expect(client).toBeInstanceOf(WaveClient);
    });

    test('logData returns expected format', async () => {
        const client = new WaveClient();
        const result = await client.logData('test-exp-123', 'participant-001', { test: 'data' });
        expect(result).toContain('test-exp-123');
        expect(result).toContain('participant-001');
        expect(typeof result).toBe('string');
    });
});
