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
  import { WaveClient } from 'https://cdn.jsdelivr.net/gh/WAVE-Lab-Williams/wave-client@v1.0.0/javascript/dist/wave-client.esm.js';

  const client = new WaveClient();  // Auto-extracts API key from URL ?key=exp_abc123

  // Save data from your experiment
  await client.logExperimentData(experimentId, participantId, {
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

# Get all your experiment data as a pandas DataFrame
experiment_data = client.experiment_data.list_as_dataframe(experiment_id=123)
print(experiment_data.head())

# Get experiments and experiment types
experiments = client.experiments.list_as_dataframe()
experiment_types = client.experiment_types.list_as_dataframe()

# Advanced search across all data
search_results = client.search.experiments_as_dataframe("stroop task")
```

## Installation

### For Experiments (JavaScript)
**No installation needed!** Just use the CDN link above.

### For Data Analysis (Python)

#### Install from GitHub Releases (Recommended)

**Step 1: Install uv**
First, install [uv](https://docs.astral.sh/uv/getting-started/installation/#installing-uv) (a fast Python package manager) by following the official installation instructions.

**Step 2: Create a new Python project**
```bash
# Create and initialize a new Python project
uv init my-wave-analysis
cd my-wave-analysis

# Add the WAVE client to your project
uv add https://github.com/WAVE-Lab-Williams/wave-client/releases/latest/download/wave_client-1.0.0-py3-none-any.whl
```

**Step 3: Use your environment**

Choose one of these options:

**Option A: Run Python scripts**
```bash
# Run your analysis script
uv run python my_analysis.py
```

**Option B: Use in VS Code notebooks**
1. Open VS Code in your project folder: `code .`
2. Create a new Jupyter notebook (`.ipynb` file)
3. When prompted to select a kernel, choose the Python interpreter from your `my-wave-analysis` folder
4. The kernel will be something like `Python 3.x.x ('.venv': venv) ./venv/bin/python`

**Option C: Activate the virtual environment**
```bash
# Activate the environment for interactive use
source .venv/bin/activate  # On macOS/Linux
# or
.venv\Scripts\activate     # On Windows

# Now you can use python directly
python
>>> from wave_client import WaveClient
>>> # Your analysis code here...
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
# Install nvm - follow the instructions at:
# https://github.com/nvm-sh/nvm

# Install and use the project's specified Node.js version (from .nvmrc)
nvm use             # This reads .nvmrc and installs/uses Node.js 20 LTS

# Set up the complete development environment
make setup-local-dev
```

### Repository Structure

```
wave-client/
├── README.md                # This file
├── CLAUDE.md               # Detailed development instructions
├── package.json            # JavaScript dependencies & scripts
├── pyproject.toml          # Python dependencies & project config
├── Makefile               # Development commands
├── docs/                  # Documentation
├── javascript/            # JavaScript client
│   ├── dist/             # Built files (ESM, UMD, minified)
│   ├── src/              # Source code
│   ├── tests/            # Test suites
│   │   ├── small/        # Unit tests (fast, mocked)
│   │   └── medium/       # Integration tests (real API)
│   └── examples/         # Usage examples
└── python/               # Python client  
    ├── wave_client/      # Main package
    │   ├── resources/    # API resource classes
    │   ├── models/       # Data models
    │   └── utils/        # Utilities
    └── tests/           # Test suites
        ├── small/       # Unit tests
        └── medium/      # Integration tests
```

### Development Commands

```bash
# Setup and building
make setup-local-dev    # Complete environment setup (Python + JS + git hooks)
make setup-js          # JavaScript dependencies only
make setup             # Python environment + JS dependencies

# Testing
make test-small        # Fast tests (Python small + JS small)
make test-all          # All tests (Python + JS)
make test-python-small # Python unit tests only
make test-python-all   # All Python tests (small + medium)
make test-js           # All JavaScript tests
make test-js-small     # JavaScript unit tests only
make test-js-medium    # JavaScript integration tests only

# Code quality
make format           # Format all code (Python + JS)
make format-python    # Python formatting (isort, black, flake8, pylint)
make format-js        # JavaScript formatting
make ci               # Full CI pipeline (format + test-all)

# Building
make build-js         # Build JavaScript distribution files
make build-js-watch   # Build JS with auto-rebuild on changes

# Cleanup
make clean           # Remove build artifacts, cache files, etc.
```

## More Help

- [Installation Guide](docs/installation.md) - Detailed setup instructions for both JavaScript and Python
- [Examples](docs/examples.md) - Working examples of experiments and data analysis
- [API Reference](docs/api-reference.md) - Complete method documentation

Need help? Contact Prof. Kim Wong.

---

*This is an internal research tool for the WAVE Lab.*
