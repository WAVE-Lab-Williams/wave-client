# Client Schema Definitions

This document defines the data types and schemas used by both JavaScript and Python WAVE clients.

## JavaScript Client (Simplified - Experiment Data Only)

The JavaScript client has one primary purpose: logging experiment data during experiments. It focuses on the single most critical endpoint for data collection.

### Primary Method: `logExperimentData()`

**Purpose**: Add experiment data row during experiment execution  
**Endpoint**: `POST /api/v1/experiment-data/{experiment_id}/data/`  
**Authentication**: EXPERIMENTEE role (via URL parameter `?key=exp_abc123`)

#### Input Parameters
```javascript
// Method signature
logExperimentData(experimentId, participantId, data)

// Example usage
const result = await waveClient.logExperimentData(
  "550e8400-e29b-41d4-a716-446655440000",  // experiment UUID
  "SUBJ-2024-001",                          // participant ID
  {                                         // experiment data
    reaction_time: 1.23,
    accuracy: 0.85,
    difficulty_level: 2,
    stimulus_type: "visual"
  }
);
```

#### Request Body Format
```javascript
{
  participant_id: "SUBJ-2024-001",    // string, required, max 100 chars
  data: {                             // object, required
    // Custom fields based on experiment type schema
    reaction_time: 1.23,              // matches schema definition
    accuracy: 0.85,                   // matches schema definition
    difficulty_level: 2,              // matches schema definition
    stimulus_type: "visual"           // matches schema definition
  }
}
```

#### Response Format
```javascript
{
  id: 1,                                          // auto-generated row ID
  experiment_uuid: "550e8400-e29b-41d4-a716-446655440000",
  participant_id: "SUBJ-2024-001",
  created_at: "2024-01-15T10:30:00Z",           // ISO date string
  updated_at: "2024-01-15T10:30:00Z",           // ISO date string
  reaction_time: 1.23,                           // your custom data
  accuracy: 0.85,                                // your custom data
  difficulty_level: 2,                           // your custom data
  stimulus_type: "visual"                        // your custom data
}
```

#### Error Handling
```javascript
// Error object structure
{
  name: "WaveClientError",
  message: "Descriptive error message",
  statusCode: 400,                    // HTTP status code
  detail: "Validation error details", // server error detail
  retryAfter: 5000                   // milliseconds to wait before retry (if applicable)
}

// Common error scenarios
// 400 - Bad Request: invalid data, validation errors
// 401 - Unauthorized: missing/invalid API key
// 403 - Forbidden: wrong role (need EXPERIMENTEE+)
// 404 - Not Found: experiment doesn't exist
// 500 - Internal Server Error: server issues
```

#### jsPsych Integration
```javascript
// Direct integration with jsPsych trial data
const trialData = jsPsych.data.get().last(1).values()[0];

await waveClient.logExperimentData(
  experimentId,
  participantId,
  {
    reaction_time: trialData.rt,
    response: trialData.response,
    stimulus: trialData.stimulus,
    correct: trialData.correct
  }
);
```

## Python Client (Full API Access)

The Python client provides complete access to all API endpoints, organized into resource classes with pandas integration.

### Core Data Types

#### Column Types
```python
# Supported data types for experiment schemas
COLUMN_TYPES = [
    "INTEGER",    # Whole numbers
    "FLOAT",      # Decimal numbers  
    "STRING",     # Text (up to 255 characters)
    "TEXT",       # Long text
    "BOOLEAN",    # True/false values
    "DATETIME",   # datetime objects
    "JSON"        # dict/list objects
]
```

### Request Schemas

#### Tag Operations
```python
# Create tag
tag_data = {
    "name": "cognitive",                              # str, required, max 100 chars
    "description": "Cognitive performance experiments" # str, optional
}

# Update tag (partial)
tag_update = {
    "name": "updated_cognitive",    # str, optional
    "description": "Updated desc"   # str, optional
}
```

#### Experiment Type Operations
```python
# Create experiment type
experiment_type_data = {
    "name": "cognitive_assessment",           # str, required, max 100 chars, unique
    "description": "Cognitive evaluation",   # str, optional
    "table_name": "cognitive_test_data",     # str, required, max 100 chars, unique
    "schema_definition": {                   # dict, required
        "reaction_time": "FLOAT",
        "accuracy": "FLOAT",
        "difficulty_level": "INTEGER",
        "stimulus_type": "STRING"
    }
}

# Alternative schema definition with column options
experiment_type_data = {
    "name": "memory_test",
    "table_name": "memory_data",
    "schema_definition": {
        "score": {
            "type": "INTEGER",
            "nullable": False
        },
        "completion_time": "FLOAT",
        "errors": "INTEGER"
    }
}
```

#### Experiment Operations
```python
# Create experiment
experiment_data = {
    "experiment_type_id": 1,                    # int, required, must exist
    "description": "Visual stimuli assessment", # str, required
    "tags": ["cognitive", "visual"],           # list[str], max 10 items
    "additional_data": {                       # dict, flexible metadata
        "session_duration": 30,
        "difficulty_level": 2,
        "notes": "First session"
    }
}

# Update experiment (partial)
experiment_update = {
    "description": "Updated description",      # str, optional
    "tags": ["cognitive", "visual", "new"],   # list[str], optional
    "additional_data": {"new_field": "value"} # dict, optional
}
```

#### Experiment Data Operations
```python
# Create data row
data_row = {
    "participant_id": "SUBJ-2024-001",        # str, required, max 100 chars
    "data": {                                 # dict, required
        "reaction_time": 1.23,
        "accuracy": 0.85,
        "difficulty_level": 2,
        "stimulus_type": "visual"
    }
}

# Query data with filters
query_request = {
    "participant_id": "SUBJ-2024-001",        # str, optional filter
    "filters": {                              # dict, custom column filters
        "difficulty_level": 2,
        "accuracy": 0.85
    },
    "created_after": "2024-01-01T00:00:00",   # str, ISO date, optional
    "created_before": "2024-12-31T23:59:59",  # str, ISO date, optional
    "limit": 100,                             # int, 1-1000, default 100
    "offset": 0                               # int, default 0
}
```

### Response Schemas

#### Basic Responses
```python
# Tag response
{
    "id": 1,
    "name": "cognitive",
    "description": "Cognitive experiments",
    "created_at": "2024-01-15T10:30:00Z",     # ISO date string
    "updated_at": "2024-01-15T10:30:00Z"      # ISO date string
}

# Experiment type response
{
    "id": 1,
    "name": "cognitive_assessment",
    "description": "Cognitive evaluation",
    "table_name": "cognitive_test_data",
    "schema_definition": {
        "reaction_time": "FLOAT",
        "accuracy": "FLOAT"
    },
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
}

# Experiment response (includes nested experiment_type)
{
    "uuid": "550e8400-e29b-41d4-a716-446655440000",  # UUID string
    "experiment_type_id": 1,
    "description": "Visual stimuli assessment",
    "tags": ["cognitive", "visual"],
    "additional_data": {"session_duration": 30},
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z",
    "experiment_type": {                             # nested object
        "id": 1,
        "name": "cognitive_assessment",
        # ... full experiment type data
    }
}
```

#### Data Row Response
```python
# Experiment data row (dynamic schema based on experiment type)
{
    "id": 1,                                         # int, auto-generated
    "experiment_uuid": "550e8400-e29b-41d4-a716-446655440000",
    "participant_id": "SUBJ-2024-001",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z",
    # Custom fields based on experiment type schema
    "reaction_time": 1.23,
    "accuracy": 0.85,
    "difficulty_level": 2,
    "stimulus_type": "visual"
}
```

#### Search Responses
```python
# Search experiments by tags
{
    "experiments": [                    # list of experiment objects
        {
            "uuid": "...",
            "description": "...",
            # ... full experiment data
        }
    ],
    "total": 150,                      # int, total matching results
    "pagination": {                    # dict, pagination info
        "skip": 0,
        "limit": 100,
        "total": 150
    }
}

# Get experiment data by tags (rich response with metadata)
{
    "data": [                          # list of data rows from all matching experiments
        {
            "id": 1,
            "experiment_uuid": "...",
            "participant_id": "...",
            "reaction_time": 1.23,
            # ... experiment data fields
            # Note: includes experiment metadata for context
        }
    ],
    "total_rows": 500,                 # int, total data rows returned
    "total_experiments": 5,            # int, total experiments matched
    "experiment_info": {               # dict, metadata per experiment UUID
        "550e8400-e29b-41d4-a716-446655440000": {
            "description": "Visual stimuli assessment",
            "type_name": "cognitive_assessment",
            "tags": ["cognitive", "visual"],
            "data_count": 30
        }
    },
    "pagination": {
        "skip": 0,
        "limit": 500,
        "total": 500
    }
}
```

### Pandas Integration

#### DataFrame Conversion
```python
# Convert experiment data to pandas DataFrame
data_rows = await client.experiment_data.get_data(experiment_id)
df = client.to_dataframe(data_rows)

# DataFrame will have columns:
# - id (int)
# - experiment_uuid (str) 
# - participant_id (str)
# - created_at (datetime)
# - updated_at (datetime)
# - reaction_time (float) - custom column
# - accuracy (float) - custom column
# - difficulty_level (int) - custom column
# - stimulus_type (str) - custom column

# Advanced search with DataFrame conversion
search_result = await client.search.experiment_data_by_tags(
    tags=["cognitive", "memory"],
    match_all=True
)
df = client.to_dataframe(search_result["data"])
# DataFrame includes experiment metadata in additional columns
```

## Common Patterns

### Authentication

#### JavaScript Client (Browser-based)
```javascript
// URL parameter extraction (automatic)
// https://experiment-site.com/task.html?key=exp_abc123

// Or explicit API key option
const client = new WaveClient({ 
  apiKey: "exp_abc123"  // overrides URL parameter
});
```

#### Python Client (Server-side)
```python
# Environment variable
import os
os.environ["WAVE_API_KEY"] = "your-api-key-here"

# Or explicit in client
client = WaveClient(api_key="your-api-key-here")
```

### Error Handling
```javascript
// JavaScript - simple error handling with retries
try {
  const result = await waveClient.logExperimentData(experimentId, participantId, data);
} catch (error) {
  if (error.statusCode === 429) {
    // Rate limited - client will automatically retry
    console.log(`Rate limited, retrying in ${error.retryAfter}ms`);
  }
}
```

```python
# Python - comprehensive error handling
from wave_client.exceptions import WaveClientError, RateLimitError

try:
    result = await client.experiment_data.create(experiment_id, data_row)
except RateLimitError as e:
    # Rate limited - wait and retry
    await asyncio.sleep(e.retry_after)
except WaveClientError as e:
    # Other API errors
    print(f"API error {e.status_code}: {e.detail}")
```

### Version Compatibility
Both clients automatically send version headers and handle server compatibility responses:
- Send: `X-WAVE-Client-Version: 1.0.0`
- Receive: `X-WAVE-API-Version: 1.0.0`
- Compatibility: Same major version = compatible (1.x.x ↔ 1.y.z)