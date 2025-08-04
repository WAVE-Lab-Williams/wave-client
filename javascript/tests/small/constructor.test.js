/**
 * Constructor tests for WAVE JavaScript client
 */

import WaveClient, { AuthenticationError } from '../../src/wave-client.js';
import { TestSetup, BrowserMocks, TestHelpers } from '../test-utils.js';

describe('WaveClient Constructor', () => {
    beforeAll(() => {
        TestSetup.setupGlobalMocks();
    });

    afterAll(() => {
        TestSetup.teardownGlobalMocks();
    });

    beforeEach(() => {
        TestSetup.clearMocks();
    });

    afterEach(() => {
        BrowserMocks.restoreAll();
    });

    test('should initialize with custom configuration options', () => {
        const customClient = new WaveClient({
            apiKey: 'custom-key',
            baseUrl: 'https://api.example.com',
            timeout: 10000,
            retries: 3,
            baseDelay: 2000,
            maxDelay: 60000
        });

        expect(customClient.apiKey).toBe('custom-key');
        expect(customClient.baseUrl).toBe('https://api.example.com');
        expect(customClient.timeout).toBe(10000);
        expect(customClient.maxRetries).toBe(3);
        expect(customClient.baseDelay).toBe(2000);
        expect(customClient.maxDelay).toBe(60000);
        expect(customClient.clientVersion).toBe('1.0.0');
    });

    test('should use default configuration when options not provided', () => {
        const defaultClient = new WaveClient({ apiKey: 'test-key' });

        expect(defaultClient.apiKey).toBe('test-key');
        expect(defaultClient.baseUrl).toBe('http://localhost:8000');
        expect(defaultClient.timeout).toBe(30000);
        expect(defaultClient.maxRetries).toBe(5);
        expect(defaultClient.baseDelay).toBe(1000);
        expect(defaultClient.maxDelay).toBe(30000);
    });

    test('should automatically extract API key from URL during initialization', () => {
        BrowserMocks.setupWindowMock({ search: '?key=auto-extracted-key', hash: '' });
        BrowserMocks.setupURLSearchParamsMock(
            TestHelpers.createURLSearchParamsMock({ key: 'auto-extracted-key' })
        );

        const client = new WaveClient({ baseUrl: 'https://example.com' });

        expect(client.apiKey).toBe('auto-extracted-key');
    });

    test('should prioritize explicit API key over URL extraction', () => {
        BrowserMocks.setupWindowMock({ search: '?key=url-extracted-key', hash: '' });
        BrowserMocks.setupURLSearchParamsMock(
            TestHelpers.createURLSearchParamsMock({ key: 'url-extracted-key' })
        );

        const client = new WaveClient({
            apiKey: 'explicit-key',
            baseUrl: 'https://example.com'
        });

        expect(client.apiKey).toBe('explicit-key');
    });

    test('should extract API key from URL hash fragment during initialization', () => {
        BrowserMocks.setupWindowMock({ search: '', hash: '#key=hash-extracted-key' });
        BrowserMocks.setupURLSearchParamsMock(
            TestHelpers.createSequentialURLSearchParamsMock({}, { key: 'hash-extracted-key' })
        );

        const client = new WaveClient({ baseUrl: 'https://example.com' });
        expect(client.apiKey).toBe('hash-extracted-key');
    }); test('should throw AuthenticationError when no API key is available', () => {
        BrowserMocks.setupWindowMock({ search: '', hash: '' });

        expect(() => new WaveClient()).toThrow(AuthenticationError);
        expect(() => new WaveClient()).toThrow('API key is required. Provide apiKey option or include "key" parameter in URL.');
    });

    test('should normalize base URL by removing trailing slash', () => {
        const client = new WaveClient({
            apiKey: 'test-key',
            baseUrl: 'http://localhost:8000/'
        });

        expect(client.baseUrl).toBe('http://localhost:8000');
    });

    test('should handle base URL without trailing slash', () => {
        const client = new WaveClient({
            apiKey: 'test-key',
            baseUrl: 'http://localhost:8000'
        });

        expect(client.baseUrl).toBe('http://localhost:8000');
    });
});
