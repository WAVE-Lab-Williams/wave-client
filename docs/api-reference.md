# API Reference

The WAVE Client Library provides dual-language clients for psychology experiment data logging and analysis.

## 📖 Complete API Documentation

- **[JavaScript API Reference](javascript-api-reference.md)** - Auto-generated from JSDoc comments
- **[Python API Reference](python-api-reference.md)** - Auto-generated from Python docstrings

## Quick Overview

### JavaScript Client
*Designed for experiment data logging during browser-based experiments*

```javascript
// Import using default export syntax
import WaveClient from 'https://cdn.jsdelivr.net/gh/WAVE-Lab-Williams/wave-client@v1.0.0/javascript/dist/wave-client.esm.js';

// Auto-detects API key from URL (?key=exp_abc123)
const client = new WaveClient();

// Log experiment data
await client.logExperimentData(123, 'participant-001', {
    reaction_time: 1.234,
    correct: true,
    trial_number: 1
});
```

### Python Client  
*Full API access for data analysis with pandas integration*

```python
from wave_client import WaveClient

# Context manager usage (recommended)
async with WaveClient() as client:
    # Get experiment data as DataFrame
    df = await client.experiment_data.get_data('experiment-uuid')
    
    # Create new experiment
    exp = await client.experiments.create(
        experiment_type_id=1,
        description='My experiment'
    )
```

## Installation

See [installation.md](installation.md) for detailed setup instructions.

## Error Handling

Both clients include comprehensive error handling with specific exception types:

- `AuthenticationError`: Invalid API key or authentication issues
- `ValidationError`: Invalid request data or parameters  
- `NotFoundError`: Requested resource doesn't exist
- `RateLimitError`: API rate limit exceeded
- `ServerError`: Internal server errors

---

> **Note**: This overview is kept simple. For complete method signatures, parameters, and examples, see the auto-generated API references linked above.