# Python Client API Reference

*Auto-generated from Python docstrings and introspection*

## Quick Reference

```python
from wave_client import WaveClient

# Initialize client (uses WAVE_API_KEY environment variable)
async with WaveClient() as client:
    # Get experiment data as DataFrame
    df = await client.experiment_data.get_data('experiment-uuid')
    
    # Create new experiment
    exp = await client.experiments.create(
        experiment_type_id=1,
        description='My experiment'
    )
    
    # Add experiment data
    await client.experiment_data.create(
        experiment_id=exp['uuid'],
        participant_id='P001',
        data={'reaction_time': 1.234, 'correct': True}
    )
```

## Configuration

### Environment Variables

```bash
# Required
export WAVE_API_KEY='your-api-key-here'

# Optional (defaults to localhost for development)
export WAVE_API_URL='http://localhost:8000'
```

### Direct Configuration

```python
client = WaveClient(
    api_key='your-api-key',
    base_url='https://your-wave-backend.com'
)
```

## Resource Classes

The Python client is organized into resource classes that handle different aspects of the API:

- **`client.experiment_data`** (ExperimentDataResource): Access and manage experiment data rows
- **`client.experiments`** (ExperimentsResource): Manage experiment instances
- **`client.experiment_types`** (ExperimentTypesResource): Define experiment schemas and types
- **`client.tags`** (TagsResource): Organize experiments with labels
- **`client.search`** (SearchResource): Advanced search across all resources

Each resource class provides methods that return pandas DataFrames by default,
making data analysis straightforward. Raw dictionary data is also available.

## WaveClient

Main client for the WAVE Backend API.

This client provides access to psychology experiment data through organized
resource groups. Each resource group handles related operations and returns
pandas DataFrames for easy data analysis.

## Getting Started

The client is organized into 5 main resource groups:

- **client.experiment_types**: Manage experiment templates and schemas
- **client.experiments**: Manage individual experiment instances
- **client.experiment_data**: Access and analyze experiment results (most common)
- **client.tags**: Organize experiments with labels
- **client.search**: Find experiments and data across categories

## Basic Usage

```python
import asyncio
from wave_client import WaveClient

async def analyze_data():
    # Always use as context manager for proper cleanup
    async with WaveClient() as client:
        # Get experiment data as pandas DataFrame (ready for analysis)
        df = await client.experiment_data.get_data("experiment-uuid-here")

        # Data is immediately ready for pandas operations
        print(f"Found {len(df)} data rows")
        print(f"Participants: {df['participant_id'].nunique()}")

        # Use pandas .pipe() for analysis chains
        results = (df
            .pipe(lambda x: x[x['accuracy'] > 0.8])  # Filter high accuracy
            .groupby('participant_id')['reaction_time'].mean()  # Average by participant
        )

# Run the analysis
asyncio.run(analyze_data())
```

## Resource Group Details

### client.experiment_data (Most Important for Analysis)

This is where your experiment results live. All methods return pandas DataFrames
by default, making data analysis straightforward:

```python
# Get all data for an experiment
df = await client.experiment_data.get_data(experiment_id)

# Filter by participant
df = await client.experiment_data.get_data(experiment_id, participant_id="SUBJ-001")

# Advanced queries with custom filters
df = await client.experiment_data.query_data(experiment_id, {
    "filters": {"difficulty_level": 2, "accuracy": 0.85},
    "limit": 1000
})

# Get ALL data with automatic pagination (handles large datasets)
df = await client.experiment_data.get_all_data(experiment_id)
```

### client.experiments (Manage Experiment Instances)

```python
# Create a new experiment
exp = await client.experiments.create({
    "experiment_type_id": 1,
    "description": "Memory study with visual stimuli",
    "tags": ["memory", "visual"]
})

# List experiments (returns DataFrame)
experiments_df = await client.experiments.list_as_dataframe()

# Get experiment details
exp_info = await client.experiments.get("experiment-uuid")
```

### client.search (Find Data Across Experiments)

```python
# Find all experiments with specific tags (returns DataFrame)
cognitive_experiments = await client.search.experiments_by_tags(
    tags=["cognitive", "memory"],
    match_all=True
)

# Get data from all experiments matching tags (powerful for meta-analysis)
all_cognitive_data = await client.search.experiment_data_by_tags(
    tags=["cognitive"],
    limit=5000
)
```

### client.experiment_types (Define Experiment Templates)

```python
# Create experiment type with custom data schema
exp_type = await client.experiment_types.create({
    "name": "reaction_time_study",
    "table_name": "rt_data",
    "schema_definition": {
        "reaction_time": "FLOAT",
        "accuracy": "FLOAT",
        "stimulus_type": "STRING",
        "difficulty": "INTEGER"
    }
})

# List all experiment types
types_df = await client.experiment_types.list_as_dataframe()
```

### client.tags (Organize Experiments)

```python
# Create organizational tags
await client.tags.create({"name": "cognitive", "description": "Cognitive studies"})

# List all tags
tags_df = await client.tags.list_as_dataframe()
```

## Discovering Available Methods

Each resource group has many methods. To see what's available:

```python
# In Jupyter notebook or IPython, use tab completion:
client.experiment_data.<TAB>  # Shows all available methods

# Or use Python's built-in help:
help(client.experiment_data.get_data)  # Shows method documentation

# List all methods programmatically:
methods = [method for method in dir(client.experiment_data) if not method.startswith('_')]
print(methods)
```

## Environment Variables & Configuration

The client uses environment variables for configuration with sensible defaults:

- **WAVE_API_KEY**: Your API key (required)
- **WAVE_API_URL**: Backend URL (defaults to http://localhost:8000)

```bash
# Required - your API key
export WAVE_API_KEY="your-api-key-here"

# Optional - defaults to localhost for development
export WAVE_API_URL="http://localhost:8000"
```

### Development Setup

For local development and testing, you need:
1. **WAVE Backend running on localhost:8000** (default)
2. **ADMIN or TEST level API key** (required for full CRUD operations)

The client automatically defaults to localhost if no WAVE_API_URL is provided,
making development setup seamless.

### Production Setup

```bash
export WAVE_API_KEY="prod-api-key"
export WAVE_API_URL="https://your-wave-backend.com"
```

You can also configure the client directly:

```python
client = WaveClient(
    api_key="your-api-key-here",
    base_url="https://your-wave-backend.com"
)
```

## Error Handling

The client includes built-in retry logic and clear error messages:

```python
from wave_client.exceptions import AuthenticationError, NotFoundError

try:
    df = await client.experiment_data.get_data("invalid-experiment-id")
except NotFoundError:
    print("Experiment not found - check the experiment ID")
except AuthenticationError:
    print("Check your API key in WAVE_API_KEY environment variable")
```

## Working with Large Datasets

The client handles pagination automatically and provides pandas DataFrames
optimized for memory usage:

```python
# Automatically handles pagination for large datasets
all_data = await client.experiment_data.get_all_data(experiment_id)

# Process in chunks if memory is limited
offset = 0
batch_size = 1000
while True:
    batch = await client.experiment_data.get_data(
        experiment_id, limit=batch_size, offset=offset
    )
    if batch.empty:
        break

    # Process batch
    process_batch(batch)
    offset += batch_size
```

### Methods

```python
async def close(self):
	"""
	Close the HTTP client.
	"""
```
```python
async def get_health(self) -> dict:
	"""
	Get API health status.
	
	Returns:
	    Health status response.
	"""
```
```python
async def get_version(self) -> dict:
	"""
	Get API version and compatibility information.
	
	Returns:
	    Version response with compatibility info.
	"""
```
```python
 def to_dataframe(self, data_rows) -> pandas.core.frame.DataFrame:
	"""
	Convert experiment data rows to pandas DataFrame.
	
	This is a convenience method that provides direct access to the
	pandas conversion utility for custom use cases.
	
	Args:
	    data_rows: List of ExperimentDataRow objects or compatible data.
	
	Returns:
	    pandas DataFrame ready for analysis.
	"""
```

## ExperimentDataResource

Resource for managing experiment data.

### Methods

```python
async def count_data(self, experiment_id: str, participant_id: Optional[str] = None) -> Dict[str, Any]:
	"""
	Count data rows with filtering.
	
	Args:
	    experiment_id: Experiment ID (UUID string).
	    participant_id: Filter by participant ID.
	
	Returns:
	    Count response.
	"""
```
```python
async def create(self, experiment_id: str, participant_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
	"""
	Add new data row to experiment.
	
	Args:
	    experiment_id: Experiment ID (UUID string).
	    participant_id: Participant identifier (max 100 characters).
	    data: Experiment data matching type schema.
	
	Returns:
	    Complete data row with all fields.
	"""
```
```python
async def create_batch(self, experiment_id: str, data_rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
	"""
	Create multiple data rows efficiently.
	
	Args:
	    experiment_id: Experiment ID (UUID string).
	    data_rows: List of data row creation data. Each row should contain
	              'participant_id' and other data fields.
	
	Returns:
	    List of created data rows.
	"""
```
```python
async def delete_row(self, experiment_id: str, row_id: int) -> Dict[str, Any]:
	"""
	Delete specific data row.
	
	Args:
	    experiment_id: Experiment ID (UUID string).
	    row_id: Data row ID.
	
	Returns:
	    Delete confirmation response.
	"""
```
```python
async def get_all_data(self, experiment_id: str, batch_size: int = 1000) -> pandas.core.frame.DataFrame:
	"""
	Get all experiment data with automatic pagination as DataFrame.
	
	Args:
	    experiment_id: Experiment ID (UUID string).
	    batch_size: Size of each batch.
	
	Returns:
	    pandas DataFrame of all experiment data.
	"""
```
```python
async def get_all_data_raw(self, experiment_id: str, batch_size: int = 1000) -> List[Dict[str, Any]]:
	"""
	Get all experiment data with automatic pagination as raw data.
	
	Args:
	    experiment_id: Experiment ID (UUID string).
	    batch_size: Size of each batch.
	
	Returns:
	    List of all experiment data rows as dictionaries.
	"""
```
```python
async def get_columns(self, experiment_id: str) -> Dict[str, Any]:
	"""
	Get detailed column schema info.
	
	Args:
	    experiment_id: Experiment ID (UUID string).
	
	Returns:
	    List of column type information.
	"""
```
```python
async def get_data(self, experiment_id: str, participant_id: Optional[str] = None, created_after: Optional[datetime.datetime] = None, created_before: Optional[datetime.datetime] = None, limit: int = 100, offset: int = 0) -> pandas.core.frame.DataFrame:
	"""
	Get experiment data as pandas DataFrame.
	
	Args:
	    experiment_id: Experiment ID (UUID string).
	    participant_id: Filter by participant ID.
	    created_after: Filter by creation date (after).
	    created_before: Filter by creation date (before).
	    limit: Maximum rows to return.
	    offset: Number of rows to skip.
	
	Returns:
	    pandas DataFrame ready for .pipe() processing chains.
	"""
```
```python
async def get_data_raw(self, experiment_id: str, participant_id: Optional[str] = None, created_after: Optional[datetime.datetime] = None, created_before: Optional[datetime.datetime] = None, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
	"""
	Get experiment data as raw dictionary list.
	
	Args:
	    experiment_id: Experiment ID (UUID string).
	    participant_id: Filter by participant ID.
	    created_after: Filter by creation date (after).
	    created_before: Filter by creation date (before).
	    limit: Maximum rows to return.
	    offset: Number of rows to skip.
	
	Returns:
	    List of experiment data rows as dictionaries.
	"""
```
```python
async def get_row(self, experiment_id: str, row_id: int) -> Dict[str, Any]:
	"""
	Get specific data row by ID.
	
	Args:
	    experiment_id: Experiment ID (UUID string).
	    row_id: Data row ID.
	
	Returns:
	    Complete row data.
	"""
```
```python
async def query_data(self, experiment_id: str, query_request: Dict[str, Any]) -> pandas.core.frame.DataFrame:
	"""
	Advanced data querying with custom filters, returns DataFrame.
	
	Args:
	    experiment_id: Experiment ID (UUID string).
	    query_request: Query parameters.
	
	Returns:
	    pandas DataFrame of matching rows.
	"""
```
```python
async def query_data_raw(self, experiment_id: str, query_request: Dict[str, Any]) -> List[Dict[str, Any]]:
	"""
	Advanced data querying with custom filters, returns raw data.
	
	Args:
	    experiment_id: Experiment ID (UUID string).
	    query_request: Query parameters.
	
	Returns:
	    List of matching rows as dictionaries.
	"""
```
```python
async def update_row(self, experiment_id: str, row_id: int, participant_id: Optional[str] = None, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
	"""
	Update specific data row.
	
	Args:
	    experiment_id: Experiment ID (UUID string).
	    row_id: Data row ID.
	    participant_id: Participant identifier (max 100 characters).
	    data: Experiment data updates.
	
	Returns:
	    Updated row data.
	"""
```

## ExperimentsResource

Resource for managing experiments.

### Methods

```python
async def create(self, experiment_type_id: int, description: str, tags: Optional[List[str]] = None, additional_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
	"""
	Create a new experiment.
	
	Args:
	    experiment_type_id: Experiment type ID (must be > 0).
	    description: Experiment description.
	    tags: List of tags (max 10).
	    additional_data: Additional metadata.
	
	Returns:
	    Created experiment response.
	"""
```
```python
async def delete(self, experiment_uuid: str) -> Dict[str, Any]:
	"""
	Delete experiment (requires ADMIN role).
	
	Args:
	    experiment_uuid: Experiment UUID.
	
	Returns:
	    Delete confirmation response.
	"""
```
```python
async def get(self, experiment_uuid: str) -> Dict[str, Any]:
	"""
	Get experiment by UUID.
	
	Args:
	    experiment_uuid: Experiment UUID.
	
	Returns:
	    Experiment response.
	"""
```
```python
async def get_by_tags(self, tags: List[str], match_all: bool = True, **kwargs) -> List[Dict[str, Any]]:
	"""
	Filter experiments by tags.
	
	Args:
	    tags: List of tags to filter by.
	    match_all: Whether to match all tags (True) or any tag (False).
	    **kwargs: Additional arguments passed to list().
	
	Returns:
	    List of matching experiments.
	"""
```
```python
async def get_by_type(self, experiment_type_id: int, **kwargs) -> List[Dict[str, Any]]:
	"""
	Filter experiments by type.
	
	Args:
	    experiment_type_id: Experiment type ID.
	    **kwargs: Additional arguments passed to list().
	
	Returns:
	    List of matching experiments.
	"""
```
```python
async def get_columns(self, experiment_uuid: str) -> Dict[str, Any]:
	"""
	Get data schema information for experiment.
	
	Args:
	    experiment_uuid: Experiment UUID.
	
	Returns:
	    Experiment columns response.
	"""
```
```python
async def list(self, skip: int = 0, limit: int = 100, experiment_type_id: Optional[int] = None, tags: Optional[List[str]] = None) -> List[Dict[str, Any]]:
	"""
	List experiments with filtering.
	
	Args:
	    skip: Number of records to skip.
	    limit: Maximum number of records to return.
	    experiment_type_id: Filter by experiment type ID.
	    tags: Filter by tags.
	
	Returns:
	    List of experiment responses.
	"""
```
```python
async def list_as_dataframe(self, **kwargs) -> pandas.core.frame.DataFrame:
	"""
	List experiments as pandas DataFrame.
	
	Args:
	    **kwargs: Arguments passed to list().
	
	Returns:
	    pandas DataFrame of experiments.
	"""
```
```python
async def update(self, experiment_uuid: str, description: Optional[str] = None, tags: Optional[List[str]] = None, additional_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
	"""
	Update experiment.
	
	Args:
	    experiment_uuid: Experiment UUID.
	    description: Experiment description.
	    tags: List of tags (max 10).
	    additional_data: Additional metadata.
	
	Returns:
	    Updated experiment response.
	"""
```

## ExperimentTypesResource

Resource for managing experiment types.

### Methods

```python
async def create(self, name: str, table_name: str, schema_definition: Optional[Dict[str, Any]] = None, description: Optional[str] = None) -> Dict[str, Any]:
	"""
	Create a new experiment type.
	
	Args:
	    name: Experiment type name (max 100 characters).
	    table_name: Database table name (max 100 characters).
	    schema_definition: Column definitions for experiment data.
	    description: Experiment type description.
	
	Returns:
	    Created experiment type response.
	"""
```
```python
async def delete(self, experiment_type_id: int) -> Dict[str, Any]:
	"""
	Delete experiment type.
	
	Args:
	    experiment_type_id: Experiment type ID.
	
	Returns:
	    Delete confirmation response.
	"""
```
```python
async def get(self, experiment_type_id: int) -> Dict[str, Any]:
	"""
	Get experiment type by ID.
	
	Args:
	    experiment_type_id: Experiment type ID.
	
	Returns:
	    Experiment type response.
	"""
```
```python
async def get_columns_by_name(self, experiment_type_name: str) -> Dict[str, Any]:
	"""
	Get schema information for experiment type by name.
	
	Args:
	    experiment_type_name: Experiment type name.
	
	Returns:
	    Experiment columns response.
	"""
```
```python
async def list(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
	"""
	List experiment types with pagination.
	
	Args:
	    skip: Number of records to skip.
	    limit: Maximum number of records to return.
	
	Returns:
	    List of experiment type responses.
	"""
```
```python
async def list_as_dataframe(self, **kwargs) -> pandas.core.frame.DataFrame:
	"""
	List experiment types as pandas DataFrame.
	
	Args:
	    **kwargs: Arguments passed to list().
	
	Returns:
	    pandas DataFrame of experiment types.
	"""
```
```python
async def update(self, experiment_type_id: int, name: Optional[str] = None, description: Optional[str] = None, schema_definition: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
	"""
	Update experiment type.
	
	Args:
	    experiment_type_id: Experiment type ID.
	    name: Experiment type name (max 100 characters).
	    description: Experiment type description.
	    schema_definition: Column definitions.
	
	Returns:
	    Updated experiment type response.
	"""
```

## TagsResource

Resource for managing tags.

### Methods

```python
async def create(self, name: str, description: Optional[str] = None) -> Dict[str, Any]:
	"""
	Create a new tag.
	
	Args:
	    name: Tag name (max 100 characters).
	    description: Tag description.
	
	Returns:
	    Created tag response.
	"""
```
```python
async def delete(self, tag_id: int) -> Dict[str, Any]:
	"""
	Delete tag.
	
	Args:
	    tag_id: Tag ID.
	
	Returns:
	    Delete confirmation response.
	"""
```
```python
async def get(self, tag_id: int) -> Dict[str, Any]:
	"""
	Get tag by ID.
	
	Args:
	    tag_id: Tag ID.
	
	Returns:
	    Tag response.
	"""
```
```python
async def list(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
	"""
	List tags with pagination.
	
	Args:
	    skip: Number of records to skip.
	    limit: Maximum number of records to return.
	
	Returns:
	    List of tag responses.
	"""
```
```python
async def list_as_dataframe(self, **kwargs) -> pandas.core.frame.DataFrame:
	"""
	List tags as pandas DataFrame.
	
	Args:
	    **kwargs: Arguments passed to list().
	
	Returns:
	    pandas DataFrame of tags.
	"""
```
```python
async def update(self, tag_id: int, name: Optional[str] = None, description: Optional[str] = None) -> Dict[str, Any]:
	"""
	Update tag.
	
	Args:
	    tag_id: Tag ID.
	    name: Tag name (max 100 characters).
	    description: Tag description.
	
	Returns:
	    Updated tag response.
	"""
```

## SearchResource

Resource for advanced search across all resources.

### Methods

```python
async def experiment_data_by_tags(self, tags: List[str], match_all: bool = True, created_after: Optional[datetime.datetime] = None, created_before: Optional[datetime.datetime] = None, skip: int = 0, limit: int = 500) -> pandas.core.frame.DataFrame:
	"""
	Get experiment data for experiments matching tags.
	
	Args:
	    tags: Tags to search for.
	    match_all: Match ALL tags (True) or ANY tag (False).
	    created_after: Filter by creation date (after).
	    created_before: Filter by creation date (before).
	    skip: Number of records to skip.
	    limit: Maximum data rows to return.
	
	Returns:
	    pandas DataFrame of experiment data with metadata.
	"""
```
```python
async def experiment_types_by_description(self, search_text: str, created_after: Optional[datetime.datetime] = None, created_before: Optional[datetime.datetime] = None, skip: int = 0, limit: int = 100) -> pandas.core.frame.DataFrame:
	"""
	Search experiment types by description.
	
	Args:
	    search_text: Text to search for.
	    created_after: Filter by creation date (after).
	    created_before: Filter by creation date (before).
	    skip: Number of records to skip.
	    limit: Maximum number of records to return.
	
	Returns:
	    pandas DataFrame of matching experiment types.
	"""
```
```python
async def experiments_advanced(self, search_text: Optional[str] = None, tags: Optional[List[str]] = None, match_all_tags: bool = True, experiment_type_id: Optional[int] = None, created_after: Optional[datetime.datetime] = None, created_before: Optional[datetime.datetime] = None, skip: int = 0, limit: int = 100) -> pandas.core.frame.DataFrame:
	"""
	Advanced experiment search with multiple criteria.
	
	Args:
	    search_text: Text search in descriptions.
	    tags: Tag filters.
	    match_all_tags: Match ALL tags (True) or ANY tag (False).
	    experiment_type_id: Filter by experiment type.
	    created_after: Filter by creation date (after).
	    created_before: Filter by creation date (before).
	    skip: Number of records to skip.
	    limit: Maximum number of records to return.
	
	Returns:
	    pandas DataFrame of matching experiments.
	"""
```
```python
async def experiments_by_description_and_type(self, experiment_type_id: int, search_text: str, created_after: Optional[datetime.datetime] = None, created_before: Optional[datetime.datetime] = None, skip: int = 0, limit: int = 100) -> pandas.core.frame.DataFrame:
	"""
	Search experiment descriptions within specific type.
	
	Args:
	    experiment_type_id: Experiment type ID.
	    search_text: Text to search for.
	    created_after: Filter by creation date (after).
	    created_before: Filter by creation date (before).
	    skip: Number of records to skip.
	    limit: Maximum number of records to return.
	
	Returns:
	    pandas DataFrame of matching experiments.
	"""
```
```python
async def experiments_by_tags(self, tags: List[str], match_all: bool = True, created_after: Optional[datetime.datetime] = None, created_before: Optional[datetime.datetime] = None, skip: int = 0, limit: int = 100) -> pandas.core.frame.DataFrame:
	"""
	Find experiments by tag criteria.
	
	Args:
	    tags: Tags to search for.
	    match_all: Match ALL tags (True) or ANY tag (False).
	    created_after: Filter by creation date (after).
	    created_before: Filter by creation date (before).
	    skip: Number of records to skip.
	    limit: Maximum number of records to return.
	
	Returns:
	    pandas DataFrame of matching experiments.
	"""
```
```python
async def tags_by_name(self, search_text: str, created_after: Optional[datetime.datetime] = None, created_before: Optional[datetime.datetime] = None, skip: int = 0, limit: int = 100) -> pandas.core.frame.DataFrame:
	"""
	Search tags by name/description.
	
	Args:
	    search_text: Text to search for.
	    created_after: Filter by creation date (after).
	    created_before: Filter by creation date (before).
	    skip: Number of records to skip.
	    limit: Maximum number of records to return.
	
	Returns:
	    pandas DataFrame of matching tags.
	"""
```

## Exception Classes

The client includes comprehensive error handling with specific exception types:

### `AuthenticationError`

Raised when API key is missing or invalid.

### `AuthorizationError`

Raised when API key doesn't have sufficient permissions.

### `NotFoundError`

Raised when requested resource doesn't exist.

### `RateLimitError`

Raised when request is rate limited.

### `ServerError`

Raised when server returns 5xx error.

### `ValidationError`

Raised when request data fails validation.

### `WaveClientError`

Base exception for all WAVE client errors.

### Usage Example

```python
from wave_client.exceptions import AuthenticationError, NotFoundError

try:
    data = await client.experiment_data.get_data('invalid-id')
except NotFoundError:
    print('Experiment not found')
except AuthenticationError:
    print('Check your API key')
```
