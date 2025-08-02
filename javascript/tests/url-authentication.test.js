/**
 * URL Parameter Authentication tests for WAVE JavaScript client
 */

import WaveClient from '../src/wave-client.js';
import { TestSetup, BrowserMocks, TestHelpers } from './test-utils.js';

describe('WaveClient URL Parameter Authentication', () => {
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

    afterEach(() => {
        BrowserMocks.restoreAll();
    });

    describe('Query Parameter Extraction', () => {
        test('should extract API key from query string (?key=value)', () => {
            BrowserMocks.setupWindowMock({ search: '?key=query-api-key', hash: '' });
            BrowserMocks.setupURLSearchParamsMock(
                TestHelpers.createURLSearchParamsMock({ key: 'query-api-key' })
            );

            const extractedKey = client._getApiKeyFromUrl();
            expect(extractedKey).toBe('query-api-key');
        });

        test('should extract API key from complex query string with multiple parameters', () => {
            BrowserMocks.setupWindowMock({
                search: '?participant=P001&key=complex-api-key&session=123',
                hash: ''
            });
            BrowserMocks.setupURLSearchParamsMock(
                TestHelpers.createURLSearchParamsMock({
                    participant: 'P001',
                    key: 'complex-api-key',
                    session: '123'
                })
            );

            const extractedKey = client._getApiKeyFromUrl();
            expect(extractedKey).toBe('complex-api-key');
        });
    });

    describe('Hash Fragment Extraction', () => {
        test('should extract API key from hash fragment when query is empty', () => {
            BrowserMocks.setupWindowMock({ search: '', hash: '#key=hash-api-key' });
            BrowserMocks.setupURLSearchParamsMock(
                TestHelpers.createSequentialURLSearchParamsMock({}, { key: 'hash-api-key' })
            );

            const extractedKey = client._getApiKeyFromUrl();
            expect(extractedKey).toBe('hash-api-key');
        });

        test('should handle hash fragment with multiple parameters', () => {
            BrowserMocks.setupWindowMock({
                search: '',
                hash: '#experiment=exp123&key=hash-complex-key&mode=test'
            });
            BrowserMocks.setupURLSearchParamsMock(
                TestHelpers.createSequentialURLSearchParamsMock(
                    {},
                    { experiment: 'exp123', key: 'hash-complex-key', mode: 'test' }
                )
            );

            const extractedKey = client._getApiKeyFromUrl();
            expect(extractedKey).toBe('hash-complex-key');
        });
    });

    describe('Parameter Priority and Fallback', () => {
        test('should prioritize query parameters over hash parameters', () => {
            BrowserMocks.setupWindowMock({
                search: '?key=query-priority',
                hash: '#key=hash-fallback'
            });
            BrowserMocks.setupURLSearchParamsMock(
                TestHelpers.createURLSearchParamsMock({ key: 'query-priority' })
            );

            const extractedKey = client._getApiKeyFromUrl();
            expect(extractedKey).toBe('query-priority');
        });

        test('should return null when key parameter is not found in either location', () => {
            BrowserMocks.setupWindowMock({
                search: '?other=value',
                hash: '#another=value'
            });
            BrowserMocks.setupURLSearchParamsMock(
                TestHelpers.createSequentialURLSearchParamsMock({}, {})
            );

            const extractedKey = client._getApiKeyFromUrl();
            expect(extractedKey).toBeNull();
        });
    });

    describe('Edge Cases and Error Handling', () => {
        test('should handle special characters in API key', () => {
            BrowserMocks.setupWindowMock({ search: '?key=exp_abc-123_DEF', hash: '' });
            BrowserMocks.setupURLSearchParamsMock(
                TestHelpers.createURLSearchParamsMock({ key: 'exp_abc-123_DEF' })
            );

            const extractedKey = client._getApiKeyFromUrl();
            expect(extractedKey).toBe('exp_abc-123_DEF');
        });

        test('should return null when not in browser environment', () => {
            delete global.window;
            const extractedKey = client._getApiKeyFromUrl();
            expect(extractedKey).toBeNull();
        });

        test('should return null when URLSearchParams is not available', () => {
            BrowserMocks.setupWindowMock({ search: '?key=test-key', hash: '' });
            delete global.URLSearchParams;

            const extractedKey = client._getApiKeyFromUrl();
            expect(extractedKey).toBeNull();
        });

        test('should handle URLSearchParams constructor errors gracefully', () => {
            BrowserMocks.setupWindowMock({ search: '?key=test-key', hash: '' });
            global.URLSearchParams = jest.fn().mockImplementation(() => {
                throw new Error('URLSearchParams constructor failed');
            });

            const extractedKey = client._getApiKeyFromUrl();
            expect(extractedKey).toBeNull();
        });

        test('should handle URLSearchParams.get() method errors gracefully', () => {
            BrowserMocks.setupWindowMock({ search: '?key=test-key', hash: '' });
            global.URLSearchParams = jest.fn().mockImplementation(() => ({
                get: jest.fn(() => {
                    throw new Error('get() method failed');
                })
            }));

            const extractedKey = client._getApiKeyFromUrl();
            expect(extractedKey).toBeNull();
        });
    });

    describe('Integration with Constructor', () => {
        test('should use extracted API key during client initialization', () => {
            BrowserMocks.setupWindowMock({ search: '?key=constructor-integration-key', hash: '' });
            BrowserMocks.setupURLSearchParamsMock(
                TestHelpers.createURLSearchParamsMock({ key: 'constructor-integration-key' })
            );

            const client = new WaveClient({ baseUrl: 'https://test.com' });
            expect(client.apiKey).toBe('constructor-integration-key');
        });
    });
});
