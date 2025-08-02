# Installation Guide

## For Running Experiments (JavaScript)

### Quick Start (Recommended)
Just copy this into your HTML experiment - no installation needed:

```html
<script type="module">
  import { WaveClient } from 'https://cdn.jsdelivr.net/gh/WAVE-Lab-Williams/wave-client@v1.0.0/wave-client.esm.js';

  const client = new WaveClient();
  // Your experiment code here
</script>
```

**Important:** Replace `v1.0.0` with the latest version from our [releases page](https://github.com/WAVE-Lab-Williams/wave-client/releases).

### Alternative: Specific Version from Releases
For more control, download specific release files:

```html
<!-- Option 1: ES6 Module (recommended for modern browsers) -->
<script type="module">
  import { WaveClient } from 'https://cdn.jsdelivr.net/gh/WAVE-Lab-Williams/wave-client@v1.0.0/wave-client.esm.js';
</script>

<!-- Option 2: UMD for older browsers -->
<script src="https://cdn.jsdelivr.net/gh/WAVE-Lab-Williams/wave-client@v1.0.0/wave-client.umd.js"></script>
<script>
  const client = new WaveClient.WaveClient();
</script>
```

### Local Files (If CDN Unavailable)
Download from the [releases page](https://github.com/WAVE-Lab-Williams/wave-client/releases):

1. Go to the latest release
2. Download `wave-client-js-v1.0.0.zip`
3. Extract and use the files in your HTML:

```html
<script type="module">
  import { WaveClient } from './wave-client.esm.js';
</script>
```

### For JavaScript Developers

If you want to modify or build the JavaScript client locally, you'll need Node.js and npm:

#### Installing Node.js and npm via nvm (Recommended)

nvm (Node Version Manager) lets you install and manage multiple Node.js versions:

```bash
# Install nvm - follow the instructions at:
# https://github.com/nvm-sh/nvm

# Install and use the project's specified Node.js version (from .nvmrc)
nvm use             # This reads .nvmrc and installs/uses Node.js 20 LTS

# Verify installation
node --version
npm --version
```

**Note:** Visit [github.com/nvm-sh/nvm](https://github.com/nvm-sh/nvm) for the latest installation instructions and troubleshooting.

#### Alternative: Direct Node.js Installation

If you prefer not to use nvm, download Node.js directly from [nodejs.org](https://nodejs.org/) (npm is included).

#### Setting Up the Development Environment

Once you have Node.js and npm installed:

```bash
# Clone the repository
git clone https://github.com/WAVE-Lab-Williams/wave-client.git
cd wave-client

# Set up both Python and JavaScript environments
make setup-local-dev

# Or just set up JavaScript
make setup-js

# Build the JavaScript client
make build-js

# Run tests
make test-js

# Development with auto-rebuild
make build-js-watch
```

## For Data Analysis (Python)

### Install from GitHub Releases (Recommended)

Download the pre-built package from our releases:

```bash
# Option 1: Using pip
pip install https://github.com/WAVE-Lab-Williams/wave-client/releases/latest/download/wave_client-1.0.0-py3-none-any.whl

# Option 2: Using uv (faster)
uv add https://github.com/WAVE-Lab-Williams/wave-client/releases/latest/download/wave_client-1.0.0-py3-none-any.whl
```

**Note:** Replace `1.0.0` with the latest version from our [releases page](https://github.com/WAVE-Lab-Williams/wave-client/releases).

Don't have `uv`? [Install it here](https://docs.astral.sh/uv/getting-started/installation/) - it's much faster than pip.

### Install from Source (Development)

If you want to modify the Python client or use the latest unreleased features:

```bash
# Clone and install in development mode
git clone https://github.com/WAVE-Lab-Williams/wave-client.git
cd wave-client
uv pip install -e .[dev,test]

# Or with pip
pip install -e .[dev,test]
```

### Set Up Your Environment Variables

Add this to your `.env` file or set as environment variables:
```bash
WAVE_API_KEY=your-api-key-from-prof-wong
WAVE_API_URL=https://your-wave-backend.com
```

You can copy `.env.example` to `.env` and fill in your values.

## Troubleshooting

**JavaScript not working?** Make sure you're using `type="module"` in your script tag.

**Python import error?** Make sure you installed it from the releases page or run `uv add https://github.com/WAVE-Lab-Williams/wave-client/releases/latest/download/wave_client-1.0.0-py3-none-any.whl`

**API key issues?** Contact Prof. Kim Wong to get your key.

**npm/Node.js issues?**
- Make sure you've restarted your terminal after installing nvm
- Run `nvm use node` to activate the latest Node.js version
- Check that `node --version` and `npm --version` both work

**Development setup issues?** Run `make clean && make setup-local-dev` to reset everything.
