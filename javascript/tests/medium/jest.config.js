/**
 * Jest configuration for medium/integration tests
 * These tests may require external dependencies and take longer to run
 */

export default {
    displayName: 'Medium Tests (Integration)',
    testEnvironment: 'node',
    testMatch: [
        '**/javascript/tests/medium/**/*.test.js'
    ],
    transform: {
        '^.+\\.js$': 'babel-jest'
    },
    setupFilesAfterEnv: ['<rootDir>/javascript/tests/medium/setup.js'],
    testTimeout: 30000 // Longer timeout for integration tests
};
