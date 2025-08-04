/**
 * Jest configuration for small/unit tests
 * These tests should be fast and not require external dependencies
 */

export default {
    displayName: 'Small Tests (Unit)',
    testEnvironment: 'node',
    testMatch: [
        '**/javascript/tests/small/**/*.test.js'
    ],
    transform: {
        '^.+\\.js$': 'babel-jest'
    },
    setupFilesAfterEnv: ['<rootDir>/javascript/tests/small/setup.js']
};
