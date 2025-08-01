# WAVE Client

Easy-to-use tools for running psychology experiments and analyzing your data.

## What is this?

If you're running psychology experiments, this helps you:
- **Collect data** from participants during experiments (JavaScript)
- **Download and analyze** your data after experiments (Python)

## For Running Experiments (JavaScript)

Add this to your HTML experiment:

```html
<script type="module">
  import { WaveClient } from 'https://cdn.jsdelivr.net/gh/wave-lab/wave-client@latest/javascript/dist/wave-client.esm.js';
  
  const client = new WaveClient();  // Uses WAVE_API_KEY and WAVE_API_URL from environment
  
  // Save data from your experiment
  await client.logData(experimentId, participantId, {
    reaction_time: 1.23,
    correct: true,
    trial_number: 1
  });
</script>
```

## For Analyzing Data (Python)

```python
from wave_client import WaveClient

client = WaveClient()  # Uses WAVE_API_KEY and WAVE_API_URL from environment

# Get all your experiment data as a spreadsheet (DataFrame)
data = client.get_experiment_data(experiment_id)
print(data.head())
```

## Setup

1. **Get credentials** from Prof. Kim Wong (API key and backend URL)
2. **Set environment variables**: Copy `.env.example` to `.env` and fill in your values
3. **For experiments**: Copy the JavaScript code above (Vercel will handle the environment variables)
4. **For analysis**: Install Python client: `uv add git+https://github.com/wave-lab/wave-client.git` (or `pip install git+https://github.com/wave-lab/wave-client.git`)

### For Developers

If you want to modify the JavaScript client locally, you'll need Node.js and npm:

```bash
# Install Node.js via nvm (recommended)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm use             # Uses version from .nvmrc (Node.js 20 LTS)

# Set up the project
make setup-local-dev
```

## More Help

- [Installation Guide](docs/installation.md) - Detailed setup instructions
- [Examples](docs/examples.md) - Example experiments and analysis
- [API Reference](docs/api-reference.md) - Complete documentation

Need help? Contact Prof. Kim Wong.

---

*This is an internal research tool for the WAVE Lab.*