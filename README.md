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
  import { WaveClient } from 'https://cdn.jsdelivr.net/gh/WAVE-Lab-Williams/wave-client@v1.0.0/wave-client.esm.js';

  const client = new WaveClient();  // Uses WAVE_API_KEY and WAVE_API_URL from environment

  // Save data from your experiment
  await client.logData(experimentId, participantId, {
    reaction_time: 1.23,
    correct: true,
    trial_number: 1
  });
</script>
```

> **💡 Tip**: Replace `v1.0.0` with the latest version from our [releases page](https://github.com/WAVE-Lab-Williams/wave-client/releases)

## For Analyzing Data (Python)

```python
from wave_client import WaveClient

client = WaveClient()  # Uses WAVE_API_KEY and WAVE_API_URL from environment

# Get all your experiment data as a spreadsheet (DataFrame)
data = client.get_experiment_data(experiment_id)
print(data.head())
```

## Installation

### For Experiments (JavaScript)
**No installation needed!** Just use the CDN link above.

### For Data Analysis (Python)

#### Install from GitHub Releases (Recommended)
```bash
# Install latest version
pip install https://github.com/WAVE-Lab-Williams/wave-client/releases/latest/download/wave_client-1.0.0-py3-none-any.whl

# Or with uv (faster)
uv add https://github.com/WAVE-Lab-Williams/wave-client/releases/latest/download/wave_client-1.0.0-py3-none-any.whl
```

#### Install from Source (Development)
```bash
# Clone and install in development mode
git clone https://github.com/WAVE-Lab-Williams/wave-client.git
cd wave-client
uv pip install -e .[dev,test]
```

> **💡 Find the latest version**: Check our [releases page](https://github.com/WAVE-Lab-Williams/wave-client/releases) for the newest `.whl` file

## Environment Setup

1. **Get credentials** from Prof. Kim Wong (API key and backend URL)
2. **Set environment variables**:
   - **For experiments**: Add `WAVE_API_KEY` and `WAVE_API_URL` to your Vercel environment variables
   - **For analysis**: Copy `.env.example` to `.env` and fill in your values

## For Developers

If you want to modify the clients locally, you'll need Node.js and Python:

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
