# Installation Guide

## For Running Experiments (JavaScript)

### Quick Start (Recommended)

Add this to your HTML experiment - no installation needed:

```html
<script type="module">
  import { WaveClient } from 'https://cdn.jsdelivr.net/gh/WAVE-Lab-Williams/wave-client@latest/dist/wave-client.esm.js';

  const client = new WaveClient();
  // Your experiment code here
</script>
```

**Important**: Your experiment URL must include the API key:
- `https://your-site.com/experiment.html?key=exp_abc123`
- The client automatically extracts the key from the `?key=` parameter

### CDN Options

```html
<!-- Option 1: jsDelivr from GitHub (recommended) -->
<script type="module">
  import { WaveClient } from 'https://cdn.jsdelivr.net/gh/WAVE-Lab-Williams/wave-client@latest/dist/wave-client.esm.js';
</script>

<!-- Option 2: Specific version (more reliable for production) -->
<script type="module">
  import { WaveClient } from 'https://cdn.jsdelivr.net/gh/WAVE-Lab-Williams/wave-client@v1.0.0/dist/wave-client.esm.js';
</script>

<!-- Option 3: UMD for older browsers -->
<script src="https://cdn.jsdelivr.net/gh/WAVE-Lab-Williams/wave-client@latest/dist/wave-client.umd.js"></script>
<script>
  const client = new WaveClient.WaveClient();
</script>
```

### For JavaScript Developers

If you're building a JavaScript application, install directly from GitHub:

```bash
# Install from GitHub (requires built files to be committed)
npm install github:WAVE-Lab-Williams/wave-client

# Or via yarn
yarn add github:WAVE-Lab-Williams/wave-client
```

Then import in your code:
```javascript
import { WaveClient } from 'wave-client-js';
```

**Note**: This requires the built `dist/` files to be committed to the repository. For most users, the CDN approach above is simpler.

## For Data Analysis (Python)

### Install via uv (Recommended)

```bash
uv add wave-client
```

Don't have `uv`? [Install it here](https://docs.astral.sh/uv/getting-started/installation/) - it's much faster and more reliable than pip.

### Install via pip

```bash
pip install wave-client
```

### Install from Source (Development)

```bash
# Clone and install in development mode
git clone https://github.com/WAVE-Lab-Williams/wave-client.git
cd wave-client

# With uv (recommended)
uv pip install -e .[dev,test]

# Or with pip
pip install -e .[dev,test]
```

## Configuration

### Environment Variables

Add these to your environment or `.env` file:

```bash
WAVE_API_KEY=your-api-key
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
