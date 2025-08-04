"""Pandas DataFrame integration utilities for WAVE client."""

from typing import List

import pandas as pd
from wave_client.models.base import ExperimentDataRow


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
        record["experiment_uuid"] = str(record["experiment_uuid"])
        # Flatten custom data to top level
        custom_data = row.get_custom_data()
        record.update(custom_data)
        records.append(record)

    df = pd.DataFrame(records)

    # Basic type conversions for common operations
    datetime_cols = ["created_at", "updated_at"]
    for col in datetime_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col])

    # Categorical columns for memory efficiency
    categorical_cols = ["participant_id", "experiment_uuid"]
    for col in categorical_cols:
        if col in df.columns:
            df[col] = df[col].astype("category")

    return df
