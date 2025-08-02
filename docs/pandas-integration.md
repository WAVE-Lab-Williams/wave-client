# Pandas DataFrame Integration

This document defines how the Python WAVE client converts API responses to pandas DataFrames for experiment data analysis.

## Core DataFrame Conversion

### Basic Data Conversion
```python
import pandas as pd
from typing import List
from wave_client.models import ExperimentDataRow

def experiment_data_to_dataframe(data_rows: List[ExperimentDataRow]) -> pd.DataFrame:
    """
    Convert experiment data rows to pandas DataFrame.
    
    Args:
        data_rows: List of experiment data rows from API
        
    Returns:
        pandas DataFrame with experiment data ready for .pipe() chains
    """
    if not data_rows:
        return pd.DataFrame()
    
    # Convert Pydantic models to records
    records = []
    for row in data_rows:
        record = row.model_dump()
        # Convert UUID to string for DataFrame compatibility
        record['experiment_uuid'] = str(record['experiment_uuid'])
        # Flatten custom data to top level
        custom_data = row.get_custom_data()
        record.update(custom_data) 
        records.append(record)
    
    df = pd.DataFrame(records)
    
    # Basic type conversions for common operations
    datetime_cols = ['created_at', 'updated_at']
    for col in datetime_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col])
    
    # Categorical columns for memory efficiency
    categorical_cols = ['participant_id', 'experiment_uuid']
    for col in categorical_cols:
        if col in df.columns:
            df[col] = df[col].astype('category')
    
    return df
```

## Client Integration

### ExperimentDataResource with DataFrame Support
```python
class ExperimentDataResource:
    """Experiment data resource with pandas DataFrame conversion."""
    
    async def get_data_as_dataframe(
        self,
        experiment_id: str,
        participant_id: Optional[str] = None,
        created_after: Optional[datetime] = None,
        created_before: Optional[datetime] = None,
        limit: int = 1000,
        offset: int = 0
    ) -> pd.DataFrame:
        """
        Get experiment data as pandas DataFrame.
        
        Returns:
            pandas DataFrame ready for .pipe() processing chains
        """
        data_rows = await self.get_data(
            experiment_id=experiment_id,
            participant_id=participant_id,
            created_after=created_after,
            created_before=created_before,
            limit=limit,
            offset=offset
        )
        
        return experiment_data_to_dataframe(data_rows)
    
    async def query_data_as_dataframe(
        self,
        experiment_id: str,
        query_request: 'ExperimentDataQuery'
    ) -> pd.DataFrame:
        """Query experiment data and return as DataFrame."""
        data_rows = await self.query_data(experiment_id, query_request)
        return experiment_data_to_dataframe(data_rows)
    
    async def get_all_data_as_dataframe(
        self, 
        experiment_id: str,
        batch_size: int = 1000
    ) -> pd.DataFrame:
        """Get all experiment data with automatic pagination."""
        all_data = []
        offset = 0
        
        while True:
            batch = await self.get_data(
                experiment_id=experiment_id,
                limit=batch_size,
                offset=offset
            )
            
            if not batch:
                break
                
            all_data.extend(batch)
            
            if len(batch) < batch_size:
                break
                
            offset += batch_size
        
        return experiment_data_to_dataframe(all_data)
```

## Usage Examples

### Basic Usage
```python
async def get_experiment_data():
    """Get experiment data as DataFrame for analysis."""
    async with WaveClient() as client:
        # Simple data retrieval
        df = await client.experiment_data.get_data_as_dataframe(experiment_id)
        
        print(f"Retrieved {len(df)} rows with columns: {list(df.columns)}")
        return df

# With filtering
async def get_filtered_data():
    """Get filtered experiment data.""" 
    async with WaveClient() as client:
        df = await client.experiment_data.get_data_as_dataframe(
            experiment_id=experiment_id,
            participant_id="SUBJ-2024-001",
            created_after=datetime(2024, 1, 1),
            limit=5000
        )
        return df

# Using query endpoint
async def get_queried_data():
    """Get experiment data using advanced query."""
    from wave_client.models import ExperimentDataQuery
    
    async with WaveClient() as client:
        query = ExperimentDataQuery(
            filters={"difficulty_level": 2, "accuracy": 0.85},
            limit=1000
        )
        
        df = await client.experiment_data.query_data_as_dataframe(
            experiment_id, query
        )
        return df
```

### Functional Pipeline Processing
```python
# Researchers implement their own pipeline functions
def add_session_numbers(df: pd.DataFrame) -> pd.DataFrame:
    """Add session numbers grouped by participant."""
    return (df.sort_values(['participant_id', 'created_at'])
              .assign(session_number=lambda x: x.groupby('participant_id').cumcount() + 1))

def remove_outliers(df: pd.DataFrame, column: str, factor: float = 1.5) -> pd.DataFrame:
    """Remove IQR outliers from specified column."""
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - factor * IQR
    upper_bound = Q3 + factor * IQR
    return df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]

# Example analysis pipeline
async def analyze_reaction_times():
    """Example of functional data processing pipeline."""
    async with WaveClient() as client:
        results = (await client.experiment_data.get_data_as_dataframe(experiment_id)
                  .pipe(add_session_numbers)
                  .pipe(remove_outliers, column='reaction_time')
                  .pipe(lambda df: df.groupby('participant_id').agg({
                      'reaction_time': ['mean', 'std'],
                      'accuracy': 'mean',
                      'session_number': 'max'
                  })))
        
        print("Analysis results:")
        print(results)
        return results
```

### Search Integration (Optional)
```python
# For search endpoints that return experiment data
class SearchResource:
    async def experiment_data_by_tags_as_dataframe(
        self,
        tags: List[str],
        match_all: bool = True,
        **kwargs
    ) -> pd.DataFrame:
        """Search experiment data by tags and return as DataFrame."""
        search_response = await self.experiment_data_by_tags(
            tags=tags,
            match_all=match_all,
            **kwargs
        )
        
        return experiment_data_to_dataframe(search_response.data)
```

That's it! Simple, clean conversion from API to DataFrame, then researchers can build their own `.pipe()` chains for their specific analysis needs.