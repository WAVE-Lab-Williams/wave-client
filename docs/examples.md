# Examples

## JavaScript: Basic Experiment Logging

Add your API key to the URL as a query parameter: `?key=your_api_key_here`

```html
<!DOCTYPE html>
<html>
<head>
    <title>Simple Reaction Time Experiment</title>
</head>
<body>
    <div id="experiment">
        <p>Click the button when you see it turn red!</p>
        <button id="target" onclick="recordResponse()">Click Me</button>
        <div id="status">Get ready...</div>
    </div>

    <script type="module">
        import { WaveClient } from 'https://unpkg.com/wave-client@latest/dist/wave-client.esm.js';

        // Client automatically extracts API key from URL (?key=your_api_key)
        const client = new WaveClient();
        
        // Experiment configuration
        const experimentId = 123;  // Your experiment ID
        const participantId = 'participant-001';  // Unique participant ID
        
        let trialNumber = 1;
        let startTime;

        function startTrial() {
            const button = document.getElementById('target');
            const status = document.getElementById('status');
            
            // Random delay before showing target
            setTimeout(() => {
                button.style.backgroundColor = 'red';
                startTime = performance.now();
                status.textContent = 'Click now!';
            }, Math.random() * 3000 + 1000);
        }

        window.recordResponse = async function() {
            const reactionTime = (performance.now() - startTime) / 1000; // Convert to seconds
            
            try {
                await client.logExperimentData(experimentId, participantId, {
                    reaction_time: reactionTime,
                    trial_number: trialNumber,
                    timestamp: new Date().toISOString()
                });
                
                document.getElementById('status').textContent = 
                    `Trial ${trialNumber} completed! RT: ${reactionTime.toFixed(3)}s`;
                
                trialNumber++;
                
                // Reset for next trial
                setTimeout(() => {
                    document.getElementById('target').style.backgroundColor = '';
                    document.getElementById('status').textContent = 'Get ready...';
                    setTimeout(startTrial, 1000);
                }, 2000);
                
            } catch (error) {
                console.error('Failed to log data:', error);
                document.getElementById('status').textContent = 'Error logging data!';
            }
        }

        // Start first trial
        startTrial();
    </script>
</body>
</html>
```

**URL Setup**: Make sure your experiment URL includes the API key:
- ✅ `https://your-site.com/experiment.html?key=exp_abc123`
- ✅ `https://your-site.com/experiment.html?key=exp_abc123&participant=P001`

## Python: Basic Data Analysis

```python
from wave_client import WaveClient
import pandas as pd
import matplotlib.pyplot as plt

# Connect to WAVE (uses WAVE_API_KEY environment variable)
client = WaveClient()

# Get experiment data as DataFrame
experiment_id = 123
data = client.experiment_data.list_as_dataframe(experiment_id=experiment_id)

print(f"Retrieved {len(data)} data points from experiment {experiment_id}")
print("\nData overview:")
print(data.head())

# Basic statistics
if 'reaction_time' in data.columns:
    avg_rt = data['reaction_time'].mean()
    print(f"\nAverage reaction time: {avg_rt:.3f} seconds")

if 'correct' in data.columns:
    accuracy = data['correct'].mean()
    print(f"Overall accuracy: {accuracy:.2%}")

# Plot reaction time distribution
if 'reaction_time' in data.columns:
    plt.figure(figsize=(10, 6))
    plt.hist(data['reaction_time'], bins=20, alpha=0.7)
    plt.xlabel('Reaction Time (seconds)')
    plt.ylabel('Frequency')
    plt.title('Reaction Time Distribution')
    plt.show()
```

## Python: Multi-Experiment Analysis

```python
from wave_client import WaveClient
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

async with WaveClient() as client:
    # Get all experiments
    experiments = client.experiments.list_as_dataframe()
    print("Available experiments:")
    print(experiments[['id', 'name', 'description']])
    
    # Analyze specific experiments
    experiment_ids = [123, 124, 125]  # Your experiment IDs
    all_data = []
    
    for exp_id in experiment_ids:
        try:
            data = client.experiment_data.list_as_dataframe(experiment_id=exp_id)
            # Add experiment info
            exp_info = client.experiments.get(exp_id)
            data['experiment_name'] = exp_info['name']
            data['experiment_id'] = exp_id
            all_data.append(data)
            print(f"Loaded {len(data)} rows from experiment {exp_id}")
        except Exception as e:
            print(f"Failed to load experiment {exp_id}: {e}")
    
    if all_data:
        # Combine all data
        combined_data = pd.concat(all_data, ignore_index=True)
        
        # Compare experiments
        comparison = combined_data.groupby('experiment_name').agg({
            'reaction_time': ['mean', 'std', 'count'],
            'correct': 'mean'
        }).round(3)
        
        print("\nExperiment comparison:")
        print(comparison)
        
        # Visualization
        plt.figure(figsize=(12, 8))
        
        # Reaction time comparison
        plt.subplot(2, 2, 1)
        sns.boxplot(data=combined_data, x='experiment_name', y='reaction_time')
        plt.title('Reaction Time by Experiment')
        plt.xticks(rotation=45)
        
        # Accuracy comparison
        plt.subplot(2, 2, 2)
        accuracy_by_exp = combined_data.groupby('experiment_name')['correct'].mean()
        accuracy_by_exp.plot(kind='bar')
        plt.title('Accuracy by Experiment')
        plt.ylabel('Accuracy')
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        plt.show()
```

## Python: Search and Filter Data

```python
from wave_client import WaveClient

with WaveClient() as client:
    # Search for specific experiments
    stroop_experiments = client.search.experiments_as_dataframe('stroop task')
    print("Found Stroop experiments:")
    print(stroop_experiments[['id', 'name']])
    
    # Get data with filtering
    if len(stroop_experiments) > 0:
        exp_id = stroop_experiments.iloc[0]['id']
        
        # Filter by participant
        participant_data = client.experiment_data.list_as_dataframe(
            experiment_id=exp_id,
            participant_id='participant-001'
        )
        
        # Filter by data content (search in JSON data)
        correct_responses = client.search.experiment_data_as_dataframe(
            'correct: true'
        )
        
        print(f"Participant data: {len(participant_data)} rows")
        print(f"Correct responses: {len(correct_responses)} rows")
```

## Installation

### JavaScript

Add to your HTML:
```html
<script type="module">
    import { WaveClient } from 'https://unpkg.com/wave-client@latest/dist/wave-client.esm.js';
    // Your experiment code here
</script>
```

Or install via npm:
```bash
npm install wave-client
```

### Python

```bash
pip install wave-client
```

For the latest development version:
```bash
pip install git+https://github.com/WAVE-Lab-Williams/wave-client.git
```
