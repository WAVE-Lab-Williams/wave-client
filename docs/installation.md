# Installation Guide

## For Running Experiments (JavaScript)

### Quick Start
Just copy this into your HTML experiment - no installation needed:

```html
<script type="module">
  import { WaveClient } from 'https://cdn.jsdelivr.net/gh/wave-lab/wave-client@latest/javascript/dist/wave-client.esm.js';
  
  const client = new WaveClient();
  // Your experiment code here
</script>
```

### If You Need Local Files
If you can't use the CDN, download the files:

```bash
git clone https://github.com/wave-lab/wave-client.git
# Use javascript/dist/wave-client.umd.js in your HTML
```

### For JavaScript Developers

If you want to modify or build the JavaScript client locally, you'll need Node.js and npm:

#### Installing Node.js and npm via nvm (Recommended)

nvm (Node Version Manager) lets you install and manage multiple Node.js versions:

```bash
# Install nvm - follow the instructions at:
# https://github.com/nvm-sh/nvm

# After installation, restart your terminal or run:
source ~/.bashrc  # or ~/.zshrc on macOS

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
git clone https://github.com/wave-lab/wave-client.git
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

### Install the Python Client

```bash
# Recommended: using uv (fast and reliable)
uv add git+https://github.com/wave-lab/wave-client.git

# Alternative: using pip
pip install git+https://github.com/wave-lab/wave-client.git
```

Don't have `uv`? [Install it here](https://docs.astral.sh/uv/getting-started/installation/) - it's much faster than pip.

### Set Up Your Environment Variables

Add this to your `.env` file or set as environment variables:
```bash
WAVE_API_KEY=your-api-key-from-prof-wong
WAVE_API_URL=https://your-wave-backend.com
```

You can copy `.env.example` to `.env` and fill in your values.

## Troubleshooting

**JavaScript not working?** Make sure you're using `type="module"` in your script tag.

**Python import error?** Make sure you installed it: `uv add git+https://github.com/wave-lab/wave-client.git`

**API key issues?** Contact Prof. Kim Wong to get your key.

**npm/Node.js issues?** 
- Make sure you've restarted your terminal after installing nvm
- Run `nvm use node` to activate the latest Node.js version
- Check that `node --version` and `npm --version` both work

**Development setup issues?** Run `make clean && make setup-local-dev` to reset everything.