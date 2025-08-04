"""WAVE Client Library - Main client class."""

from typing import Optional

import pandas as pd
from wave_client.resources import (
    ExperimentDataResource,
    ExperimentsResource,
    ExperimentTypesResource,
    SearchResource,
    TagsResource,
)
from wave_client.utils.http_client import HTTPClient


class WaveClient:
    """Main client for the WAVE Backend API.

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
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 30.0,
        timeout: float = 30.0,
    ):
        """Initialize WAVE client.

        Args:
            api_key: API key for authentication. If None, uses WAVE_API_KEY env var.
                    For development, use ADMIN or TEST level API key.
            base_url: Base URL for API. If None, uses WAVE_API_URL env var.
                     Defaults to http://localhost:8000 for development.
            max_retries: Maximum number of retries for failed requests.
            base_delay: Base delay in seconds for exponential backoff.
            max_delay: Maximum delay in seconds between retries.
            timeout: Request timeout in seconds.
        """
        # Initialize HTTP client
        self._http_client = HTTPClient(
            api_key=api_key,
            base_url=base_url,
            max_retries=max_retries,
            base_delay=base_delay,
            max_delay=max_delay,
            timeout=timeout,
        )

        # Initialize resource managers
        self.experiment_types = ExperimentTypesResource(self)
        self.tags = TagsResource(self)
        self.experiments = ExperimentsResource(self)
        self.experiment_data = ExperimentDataResource(self)
        self.search = SearchResource(self)

    async def __aenter__(self):
        """Async context manager entry."""
        await self._http_client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self._http_client.__aexit__(exc_type, exc_val, exc_tb)

    async def close(self):
        """Close the HTTP client."""
        await self._http_client.close()

    # Utility methods

    async def get_health(self) -> dict:
        """Get API health status.

        Returns:
            Health status response.
        """
        return await self._http_client.request("GET", "/health")

    async def get_version(self) -> dict:
        """Get API version and compatibility information.

        Returns:
            Version response with compatibility info.
        """
        return await self._http_client.request("GET", "/version")

    def to_dataframe(self, data_rows) -> pd.DataFrame:
        """Convert experiment data rows to pandas DataFrame.

        This is a convenience method that provides direct access to the
        pandas conversion utility for custom use cases.

        Args:
            data_rows: List of ExperimentDataRow objects or compatible data.

        Returns:
            pandas DataFrame ready for analysis.
        """
        from wave_client.utils.pandas_utils import experiment_data_to_dataframe

        return experiment_data_to_dataframe(data_rows)
