# API Reference

## JavaScript Client

The JavaScript client is designed for experiment data logging during experiments. It automatically extracts API keys from URL parameters for secure browser usage.

### Constructor

```javascript
// Auto-detects API key from URL (?key=exp_abc123)
const client = new WaveClient();

// Or specify options explicitly
const client = new WaveClient({
    apiKey: 'exp_abc123',           // Optional: explicit API key
    baseUrl: 'https://api.wave.com', // Optional: custom base URL
    timeout: 30000,                  // Optional: request timeout (ms)
    retries: 3                       // Optional: max retry attempts
});
```

### logExperimentData(experimentId, participantId, data)

Saves experiment data during an experiment.

```javascript
await client.logExperimentData(123, 'participant-001', {
    reaction_time: 1.234,    // Reaction time in seconds
    correct: true,           // Boolean response
    trial_number: 1,         // Trial information
    stimulus: 'red_square'   // Any custom data
});
```

### fromJsPsychData(jsPsychData)

Converts jsPsych trial data to WAVE format.

```javascript
// jsPsych trial data
const trialData = {
    rt: 1234,                    // Reaction time in milliseconds
    correct: true,
    trial_type: 'html-keyboard-response',
    stimulus: '<p>Hello</p>',
    response: 'f'
};

// Convert to WAVE format
const waveData = client.fromJsPsychData(trialData);
// Result: { reaction_time: 1.234, correct: true, trial_type: 'html-keyboard-response', ... }
```

### Utility Methods

```javascript
// Check API health
const health = await client.getHealth();

// Get API version information
const version = await client.getVersion();

// Update base URL
client.setBaseUrl('https://new-api.com');
```

## Python Client

The Python client provides full API access for data analysis, with pandas DataFrame integration.

### Constructor

```javascript
from wave_client import WaveClient

# Uses WAVE_API_KEY and WAVE_API_URL environment variables
client = WaveClient()

# Or specify options explicitly
client = WaveClient(
    api_key='your_api_key',
    base_url='https://api.wave.com',
    timeout=30.0
)
```

### Experiment Data

```python
# Get experiment data as DataFrame
data = client.experiment_data.list_as_dataframe(experiment_id=123)

# Add new data row
new_row = client.experiment_data.create(
    experiment_id=123,
    participant_id='p001',
    data={'reaction_time': 1.234, 'correct': True}
)

# Query with filters
filtered_data = client.experiment_data.list_as_dataframe(
    experiment_id=123,
    participant_id='p001',
    limit=100
)
```

### Experiments

```python
# List all experiments as DataFrame
experiments = client.experiments.list_as_dataframe()

# Get specific experiment
experiment = client.experiments.get(123)

# Create new experiment
new_exp = client.experiments.create(
    name='Stroop Task',
    description='Color-word interference study',
    experiment_type_id=1
)
```

### Experiment Types

```python
# List all experiment types
types = client.experiment_types.list_as_dataframe()

# Get specific type with schema information
exp_type = client.experiment_types.get(1)
schema = client.experiment_types.get_schema(1)
```

### Tags

```python
# List all tags
tags = client.tags.list_as_dataframe()

# Create new tag
tag = client.tags.create(
    name='cognitive',
    description='Cognitive psychology experiments'
)

# Search tags
results = client.tags.search('cognitive')
```

### Search

```python
# Search experiments by text
experiments = client.search.experiments_as_dataframe('stroop task')

# Search experiment types
types = client.search.experiment_types_as_dataframe('reaction time')

# Search experiment data
data = client.search.experiment_data_as_dataframe('correct response')

# Search tags
tags = client.search.tags_as_dataframe('cognitive')
```

### Context Manager Usage

```python
# Recommended: use as context manager for automatic cleanup
async with WaveClient() as client:
    data = await client.experiment_data.list_as_dataframe(experiment_id=123)
    # Client automatically closed when done
```

## Error Handling

Both clients include comprehensive error handling:

```javascript
// JavaScript
try {
    await client.logExperimentData(123, 'p001', data);
} catch (error) {
    if (error instanceof ValidationError) {
        console.error('Invalid data:', error.message);
    } else if (error instanceof AuthenticationError) {
        console.error('Check your API key:', error.message);
    } else if (error instanceof RateLimitError) {
        console.error('Rate limited, retry in:', error.retryAfter, 'seconds');
    }
}
```

```python
# Python
from wave_client.exceptions import ValidationError, AuthenticationError, RateLimitError

try:
    data = client.experiment_data.list_as_dataframe(experiment_id=123)
except ValidationError as e:
    print(f"Invalid request: {e}")
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
except RateLimitError as e:
    print(f"Rate limited, retry after {e.retry_after} seconds")
```