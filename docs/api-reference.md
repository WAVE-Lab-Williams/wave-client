# API Reference

## JavaScript Client

### WaveClient()

Creates a new client instance. Uses `WAVE_API_KEY` and `WAVE_API_URL` environment variables.

```javascript
const client = new WaveClient();
```

### logData(experimentId, participantId, data)

Saves experiment data.

```javascript
await client.logData('exp-123', 'participant-001', {
    reaction_time: 1234,
    correct: true,
    trial_number: 1
});
```

## Python Client

### WaveClient()

Creates a new client instance. Uses `WAVE_API_KEY` and `WAVE_API_URL` environment variables.

```python
from wave_client import WaveClient
client = WaveClient()
```

### get_experiment_data(experiment_id)

Gets all data from an experiment as a pandas DataFrame.

```python
data = client.get_experiment_data('exp-123')
print(data.head())
```

### get_experiments()

Lists all your experiments.

```python
experiments = client.get_experiments()
for exp in experiments:
    print(f"{exp['id']}: {exp['name']}")
```