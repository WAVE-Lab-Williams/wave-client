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
        import WaveClient from 'https://cdn.jsdelivr.net/gh/WAVE-Lab-Williams/wave-client@v1.0.0/javascript/dist/wave-client.esm.js';

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

View the notebooks in `wave-client/python/examples`

## Installation

### JavaScript

Add to your HTML:
```html
<script type="module">
    import { WaveClient } from 'https://cdn.jsdelivr.net/gh/WAVE-Lab-Williams/wave-client@v1.0.0/wave-client.esm.js';
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
