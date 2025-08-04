/**
 * jsPsych data tests for WAVE JavaScript client
 */

import WaveClient, { ValidationError } from '../../src/wave-client.js';
import { MOCK_DATA } from '../../test-config.js';
import { TestSetup } from '../test-utils.js';

describe('WaveClient fromJsPsychData', () => {
    beforeAll(() => {
        TestSetup.setupGlobalMocks();
    });

    afterAll(() => {
        TestSetup.teardownGlobalMocks();
    });

    beforeEach(() => {
        TestSetup.clearMocks();
    });

    describe('Data Transformation', () => {
        test('should convert jsPsych trial data to WAVE format correctly', () => {
            const result = WaveClient.fromJsPsychData(MOCK_DATA.jsPsychTrialData);

            expect(result).toEqual({
                reaction_time: 1.234, // Converted from ms to seconds
                response: 'correct',
                correct: true,
                stimulus: 'target_image.png',
                trial_type: 'image-keyboard-response',
                trial_index: 0
                // time_elapsed and internal_node_id should be filtered out
            });
        });

        test('should convert reaction time from milliseconds to seconds', () => {
            const trialData = { rt: 2500, response: 'A' }; // 2.5 seconds

            const result = WaveClient.fromJsPsychData(trialData);

            expect(result.reaction_time).toBe(2.5);
            expect(result.rt).toBeUndefined(); // Original field should not be present
        });

        test('should handle zero reaction time correctly', () => {
            const trialData = { rt: 0, response: 'immediate' };

            const result = WaveClient.fromJsPsychData(trialData);

            expect(result.reaction_time).toBe(0);
        });

        test('should handle missing rt field gracefully', () => {
            const trialData = { ...MOCK_DATA.jsPsychTrialData };
            delete trialData.rt;

            const result = WaveClient.fromJsPsychData(trialData);

            expect(result.reaction_time).toBeUndefined();
            expect(result.response).toBe('correct');
            expect(result.correct).toBe(true);
        });
    });

    describe('Field Mapping', () => {
        test('should map standard jsPsych fields to WAVE format', () => {
            const jsPsychData = {
                rt: 1500,
                response: 'ArrowLeft',
                correct: false,
                stimulus: 'left_arrow.png',
                trial_type: 'image-keyboard-response',
                trial_index: 5
            };

            const result = WaveClient.fromJsPsychData(jsPsychData);

            expect(result).toEqual({
                reaction_time: 1.5,
                response: 'ArrowLeft',
                correct: false,
                stimulus: 'left_arrow.png',
                trial_type: 'image-keyboard-response',
                trial_index: 5
            });
        });

        test('should preserve custom fields that are not in the mapping', () => {
            const customTrialData = {
                ...MOCK_DATA.jsPsychTrialData,
                custom_field: 'custom_value',
                difficulty_level: 3,
                participant_notes: 'Performed well',
                condition: 'experimental'
            };

            const result = WaveClient.fromJsPsychData(customTrialData);

            expect(result.custom_field).toBe('custom_value');
            expect(result.difficulty_level).toBe(3);
            expect(result.participant_notes).toBe('Performed well');
            expect(result.condition).toBe('experimental');
        });
    });

    describe('Field Filtering', () => {
        test('should filter out internal jsPsych fields', () => {
            const trialData = {
                rt: 1000,
                response: 'space',
                time_elapsed: 45000,
                internal_node_id: '0.0-1.2-3.0',
                custom_data: 'keep_this'
            };

            const result = WaveClient.fromJsPsychData(trialData);

            expect(result).toEqual({
                reaction_time: 1.0,
                response: 'space',
                custom_data: 'keep_this'
            });
            expect(result.time_elapsed).toBeUndefined();
            expect(result.internal_node_id).toBeUndefined();
        });

        test('should filter out fields starting with "internal_node_id"', () => {
            const trialData = {
                rt: 800,
                internal_node_id_extra: 'should_be_filtered',
                internal_node_id_data: { some: 'data' },
                normal_field: 'should_remain'
            };

            const result = WaveClient.fromJsPsychData(trialData);

            expect(result.normal_field).toBe('should_remain');
            expect(result.internal_node_id_extra).toBeUndefined();
            expect(result.internal_node_id_data).toBeUndefined();
        });
    });

    describe('Input Validation', () => {
        test('should throw ValidationError for null input', () => {
            expect(() => WaveClient.fromJsPsychData(null)).toThrow(ValidationError);
            expect(() => WaveClient.fromJsPsychData(null)).toThrow('Trial data must be an object');
        });

        test('should throw ValidationError for non-object input', () => {
            expect(() => WaveClient.fromJsPsychData('not-object')).toThrow(ValidationError);
            expect(() => WaveClient.fromJsPsychData(123)).toThrow(ValidationError);
            expect(() => WaveClient.fromJsPsychData([])).toThrow(ValidationError);
            expect(() => WaveClient.fromJsPsychData(undefined)).toThrow(ValidationError);
        });

        test('should accept empty object as valid input', () => {
            expect(() => WaveClient.fromJsPsychData({})).not.toThrow();

            const result = WaveClient.fromJsPsychData({});
            expect(result).toEqual({});
        });
    });

    describe('Edge Cases', () => {
        test('should handle non-numeric rt values gracefully', () => {
            const trialData = { rt: 'invalid', response: 'test' };

            const result = WaveClient.fromJsPsychData(trialData);

            expect(result.reaction_time).toBe('invalid'); // Pass through non-numeric values
        });

        test('should handle negative reaction times', () => {
            const trialData = { rt: -100, response: 'error' };

            const result = WaveClient.fromJsPsychData(trialData);

            expect(result.reaction_time).toBe(-0.1);
        });

        test('should handle very large objects with many fields', () => {
            const largeTrialData = {
                rt: 1000,
                response: 'space'
            };

            // Add 100 custom fields
            for (let i = 0; i < 100; i++) {
                largeTrialData[`field_${i}`] = `value_${i}`;
            }

            const result = WaveClient.fromJsPsychData(largeTrialData);

            expect(result.reaction_time).toBe(1.0);
            expect(result.response).toBe('space');
            expect(Object.keys(result)).toHaveLength(102); // rt mapped + response + 100 custom fields
        });
    });
});
