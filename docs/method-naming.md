# Method Naming Conventions

This document defines the naming conventions and API surface for both JavaScript and Python WAVE clients.

## JavaScript Client (Simplified)

The JavaScript client focuses on experiment data logging with a single primary method plus basic utilities.

### Core Methods

```javascript
class WaveClient {
  constructor(options = {}) {
    // options: { apiKey?, baseUrl?, timeout?, retries? }
  }

  // PRIMARY METHOD - Experiment Data Logging
  async logExperimentData(experimentId, participantId, data) {
    // POST /api/v1/experiment-data/{experiment_id}/data/
    // Returns: complete data row with all fields
  }

  // UTILITY METHODS
  async getHealth() {
    // GET /health
    // Returns: { status: "healthy", service: "wave-backend" }
  }

  async getVersion() {
    // GET /version  
    // Returns: version compatibility information
  }

  // HELPER METHODS
  static fromJsPsychData(trialData) {
    // Convert jsPsych trial data to WAVE format
    // Returns: formatted data object for logExperimentData()
  }

  // Configuration
  setApiKey(apiKey) {
    // Update API key (useful for environment switching)
  }

  setBaseUrl(baseUrl) {
    // Update base URL (useful for environment switching)  
  }
}
```

### Usage Examples

```javascript
// Basic usage
const client = new WaveClient();
const result = await client.logExperimentData(
  "550e8400-e29b-41d4-a716-446655440000",
  "PARTICIPANT-001", 
  {
    reaction_time: 1.23,
    accuracy: 0.85,
    response: "correct"
  }
);

// jsPsych integration
const trialData = jsPsych.data.get().last(1).values()[0];
const formattedData = WaveClient.fromJsPsychData(trialData);
await client.logExperimentData(experimentId, participantId, formattedData);

// Environment configuration
const client = new WaveClient({
  apiKey: process.env.WAVE_API_KEY,
  baseUrl: process.env.WAVE_API_URL || "http://localhost:8000",
  timeout: 30000,  // 30 seconds - generous for experiment data
  retries: 5       // 5 retries - prevent data loss
});
```

## Python Client (Full API Access)

The Python client provides comprehensive access via resource-based organization with async support.

### Client Structure

```python
class WaveClient:
    def __init__(self, api_key=None, base_url=None, timeout=None):
        # Resource managers
        self.experiment_types = ExperimentTypesResource(self)
        self.tags = TagsResource(self)  
        self.experiments = ExperimentsResource(self)
        self.experiment_data = ExperimentDataResource(self)
        self.search = SearchResource(self)
    
    # Context manager support
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    # Utility methods
    async def get_health(self):
    async def get_version(self):
    def to_dataframe(self, data):  # pandas integration
    async def close(self):
```

### Resource Classes

#### ExperimentTypesResource
```python
class ExperimentTypesResource:
    # CRUD operations
    async def create(self, experiment_type_data):
        # POST /api/v1/experiment-types/
    
    async def get(self, experiment_type_id):
        # GET /api/v1/experiment-types/{id}
    
    async def list(self, skip=0, limit=100):
        # GET /api/v1/experiment-types/
    
    async def update(self, experiment_type_id, update_data):
        # PUT /api/v1/experiment-types/{id}
    
    async def delete(self, experiment_type_id):
        # DELETE /api/v1/experiment-types/{id}
    
    async def get_columns_by_name(self, experiment_type_name):
        # GET /api/v1/experiment-types/name/{name}/columns
    
    # Pandas integration
    async def list_as_dataframe(self, **kwargs):
        # Returns: pandas DataFrame of experiment types
```

#### TagsResource
```python
class TagsResource:
    # CRUD operations
    async def create(self, tag_data):
        # POST /api/v1/tags/
    
    async def get(self, tag_id):
        # GET /api/v1/tags/{id}
    
    async def list(self, skip=0, limit=100):
        # GET /api/v1/tags/
    
    async def update(self, tag_id, update_data):
        # PUT /api/v1/tags/{id}
    
    async def delete(self, tag_id):
        # DELETE /api/v1/tags/{id}
    
    # Pandas integration
    async def list_as_dataframe(self, **kwargs):
        # Returns: pandas DataFrame of tags
```

#### ExperimentsResource
```python
class ExperimentsResource:
    # CRUD operations
    async def create(self, experiment_data):
        # POST /api/v1/experiments/
    
    async def get(self, experiment_uuid):
        # GET /api/v1/experiments/{uuid}
    
    async def list(self, skip=0, limit=100, experiment_type_id=None, tags=None):
        # GET /api/v1/experiments/
    
    async def update(self, experiment_uuid, update_data):
        # PUT /api/v1/experiments/{uuid}
        
    async def delete(self, experiment_uuid):
        # DELETE /api/v1/experiments/{uuid} - requires ADMIN role
    
    async def get_columns(self, experiment_uuid):
        # GET /api/v1/experiments/{uuid}/columns
    
    # Convenience methods
    async def get_by_tags(self, tags, match_all=True):
        # Filter experiments by tags
    
    async def get_by_type(self, experiment_type_id):
        # Filter experiments by type
    
    # Pandas integration
    async def list_as_dataframe(self, **kwargs):
        # Returns: pandas DataFrame of experiments
```

#### ExperimentDataResource
```python
class ExperimentDataResource:
    # Data operations
    async def create(self, experiment_id, data_row):
        # POST /api/v1/experiment-data/{id}/data/
    
    async def get_data(self, experiment_id, participant_id=None, 
                      created_after=None, created_before=None, 
                      limit=100, offset=0):
        # GET /api/v1/experiment-data/{id}/data/
    
    async def count_data(self, experiment_id, participant_id=None):
        # GET /api/v1/experiment-data/{id}/data/count
    
    async def get_columns(self, experiment_id):
        # GET /api/v1/experiment-data/{id}/data/columns
    
    async def get_row(self, experiment_id, row_id):
        # GET /api/v1/experiment-data/{id}/data/row/{row_id}
    
    async def update_row(self, experiment_id, row_id, update_data):
        # PUT /api/v1/experiment-data/{id}/data/row/{row_id}
        
    async def delete_row(self, experiment_id, row_id):
        # DELETE /api/v1/experiment-data/{id}/data/row/{row_id}
        
    async def query_data(self, experiment_id, query_request):
        # POST /api/v1/experiment-data/{id}/data/query
    
    # Batch operations
    async def create_batch(self, experiment_id, data_rows):
        # Create multiple data rows efficiently
    
    async def get_all_data(self, experiment_id):
        # Get all data with automatic pagination
    
    # Pandas integration
    async def get_data_as_dataframe(self, experiment_id, **kwargs):
        # Returns: pandas DataFrame of experiment data
    
    async def query_data_as_dataframe(self, experiment_id, query_request):
        # Returns: pandas DataFrame of queried data
```

#### SearchResource
```python
class SearchResource:
    # Experiment search
    async def experiments_by_tags(self, tags, match_all=True, 
                                 created_after=None, created_before=None,
                                 skip=0, limit=100):
        # POST /api/v1/search/experiments/by-tags
    
    async def experiments_by_description_and_type(self, experiment_type_id, 
                                                 search_text, **kwargs):
        # POST /api/v1/search/experiments/by-description-and-type
    
    async def experiments_advanced(self, search_text=None, tags=None, 
                                  match_all_tags=True, experiment_type_id=None,
                                  **kwargs):
        # POST /api/v1/search/experiments/advanced
    
    # Experiment type search
    async def experiment_types_by_description(self, search_text, **kwargs):
        # POST /api/v1/search/experiment-types/by-description
    
    # Tag search  
    async def tags_by_name(self, search_text, **kwargs):
        # POST /api/v1/search/tags/by-name
    
    # Data search
    async def experiment_data_by_tags(self, tags, match_all=True, **kwargs):
        # POST /api/v1/search/experiment-data/by-tags
    
    # Pandas integration - all search methods have DataFrame variants
    async def experiments_by_tags_as_dataframe(self, **kwargs):
    async def experiment_data_by_tags_as_dataframe(self, **kwargs):
    # ... etc for all search methods
```

### Usage Examples

```python
# Basic usage
async with WaveClient() as client:
    # Create experiment type
    exp_type = await client.experiment_types.create({
        "name": "memory_test",
        "table_name": "memory_data", 
        "schema_definition": {
            "word_count": "INTEGER",
            "recall_accuracy": "FLOAT"
        }
    })
    
    # Create experiment
    experiment = await client.experiments.create({
        "experiment_type_id": exp_type["id"],
        "description": "Word recall study",
        "tags": ["memory", "recall"]
    })
    
    # Add data
    data_row = await client.experiment_data.create(
        experiment["uuid"],
        {
            "participant_id": "PART-001",
            "data": {
                "word_count": 20,
                "recall_accuracy": 0.85
            }
        }
    )

# Advanced search with pandas
async with WaveClient() as client:
    # Get all cognitive experiment data as DataFrame
    df = await client.search.experiment_data_by_tags_as_dataframe(
        tags=["cognitive"],
        match_all=True
    )
    
    # Analyze results
    print(f"Total participants: {df['participant_id'].nunique()}")
    print(f"Average accuracy: {df['accuracy'].mean()}")
    
    # Filter and export
    high_performers = df[df['accuracy'] > 0.9]
    high_performers.to_csv("high_performers.csv")
```

## Naming Patterns

### JavaScript Conventions
- **Method Names**: camelCase (`logExperimentData`, `getHealth`)
- **Parameters**: camelCase (`experimentId`, `participantId`)
- **Static Methods**: PascalCase class prefix (`WaveClient.fromJsPsychData`)
- **Constants**: UPPER_SNAKE_CASE (`DEFAULT_TIMEOUT`, `MAX_RETRIES`)

### Python Conventions  
- **Method Names**: snake_case (`create_experiment`, `get_data`)
- **Class Names**: PascalCase (`WaveClient`, `ExperimentDataResource`)
- **Parameters**: snake_case (`experiment_id`, `participant_id`)
- **Private Methods**: leading underscore (`_build_request`, `_handle_error`)

### Shared Patterns
- **Resource Organization**: Both clients group related operations
- **Async Operations**: Both support async/await patterns
- **Error Handling**: Consistent error types and status codes
- **Configuration**: Environment variable support with explicit overrides

## Method Mapping

| Endpoint | JavaScript | Python |
|----------|------------|--------|
| POST /experiment-data/{id}/data/ | `logExperimentData()` | `experiment_data.create()` |
| GET /health | `getHealth()` | `get_health()` |
| GET /version | `getVersion()` | `get_version()` |
| POST /experiment-types/ | ❌ | `experiment_types.create()` |
| GET /experiments/ | ❌ | `experiments.list()` |
| POST /search/experiments/by-tags | ❌ | `search.experiments_by_tags()` |

**Legend**: ❌ = Not implemented (JavaScript focuses only on data logging)

## Extensibility

### JavaScript Client
The JavaScript client is intentionally minimal but can be extended if needed:
```javascript
// Future expansion could add:
// - getExperiment(uuid) - for basic experiment info
// - validateData(data, schema) - for client-side validation
// - batchLogData(entries) - for batch uploads
```

### Python Client
The Python client is designed for easy extension:
```python
# New resources can be added by extending BaseResource
class CustomResource(BaseResource):
    async def custom_method(self):
        return await self._client.request("GET", "/custom/endpoint")

# Client automatically supports new resources
client.custom = CustomResource(client)
```

This naming convention ensures both clients feel native to their respective ecosystems while maintaining conceptual consistency across the dual-language implementation.