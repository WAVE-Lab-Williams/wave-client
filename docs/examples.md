# Examples

## JavaScript: Simple Experiment

```html
<!DOCTYPE html>
<html>
<head>
    <title>My Experiment</title>
</head>
<body>
    <div id="experiment">
        <button onclick="recordResponse('yes')">Yes</button>
        <button onclick="recordResponse('no')">No</button>
    </div>

    <script type="module">
        import { WaveClient } from 'https://cdn.jsdelivr.net/gh/wave-lab/wave-client@latest/javascript/dist/wave-client.esm.js';
        
        const client = new WaveClient();
        const experimentId = 'your-experiment-id';
        const participantId = 'participant-001';
        
        window.recordResponse = async function(response) {
            await client.logData(experimentId, participantId, {
                response: response,
                reaction_time: Date.now() - startTime,
                trial_number: 1
            });
        }
        
        const startTime = Date.now();
    </script>
</body>
</html>
```

## Python: Get Your Data

```python
from wave_client import WaveClient
import pandas as pd

# Connect to WAVE (uses WAVE_API_KEY and WAVE_API_URL from environment)
client = WaveClient()

# Get data from one experiment
experiment_data = client.get_experiment_data('your-experiment-id')
print(f"Got {len(experiment_data)} rows of data")
print(experiment_data.head())

# Basic analysis
average_reaction_time = experiment_data['reaction_time'].mean()
accuracy = experiment_data['correct'].mean()

print(f"Average reaction time: {average_reaction_time:.2f}ms")
print(f"Accuracy: {accuracy:.2%}")
```

## Python: Multiple Experiments

```python
from wave_client import WaveClient
import pandas as pd

# Connect to WAVE (uses environment variables)
client = WaveClient()

# Get data from multiple experiments
experiment_ids = ['exp1', 'exp2', 'exp3']
all_data = []

for exp_id in experiment_ids:
    data = client.get_experiment_data(exp_id)
    data['experiment_name'] = exp_id  # Add experiment ID column
    all_data.append(data)

# Combine all experiments
combined_data = pd.concat(all_data, ignore_index=True)
print(f"Total data points: {len(combined_data)}")

# Compare across experiments
results = combined_data.groupby('experiment_name')['reaction_time'].mean()
print("Average reaction time by experiment:")
print(results)
```