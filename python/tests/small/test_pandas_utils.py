"""Unit tests for pandas DataFrame conversion utilities."""

from datetime import datetime
from uuid import UUID

import pandas as pd
from wave_client.models.base import ExperimentDataRow
from wave_client.utils.pandas_utils import experiment_data_to_dataframe


class TestExperimentDataToDataFrame:
    """Test conversion of experiment data to pandas DataFrame."""

    def test_empty_data_returns_empty_dataframe(self):
        """Test empty input returns empty DataFrame."""
        result = experiment_data_to_dataframe([])

        assert isinstance(result, pd.DataFrame)
        assert result.empty

    def test_basic_conversion_structure(self):
        """Test basic conversion creates proper DataFrame structure."""
        data_rows = [
            ExperimentDataRow(
                id=1,
                experiment_uuid=UUID("550e8400-e29b-41d4-a716-446655440000"),
                participant_id="PART-001",
                created_at=datetime(2024, 1, 15, 10, 30),
                updated_at=datetime(2024, 1, 15, 10, 30),
                reaction_time=1.23,
                accuracy=0.95,
            )
        ]

        result = experiment_data_to_dataframe(data_rows)

        # Check it's a DataFrame with correct shape
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1

        # Check required columns exist
        expected_columns = ["id", "experiment_uuid", "participant_id", "created_at", "updated_at"]
        for col in expected_columns:
            assert col in result.columns

        # Check custom data columns are flattened
        assert "reaction_time" in result.columns
        assert "accuracy" in result.columns

    def test_data_type_conversions(self):
        """Test correct data type conversions."""
        data_row = ExperimentDataRow(
            id=1,
            experiment_uuid=UUID("550e8400-e29b-41d4-a716-446655440000"),
            participant_id="PART-001",
            created_at=datetime(2024, 1, 15, 10, 30),
            updated_at=datetime(2024, 1, 15, 10, 31),
        )

        result = experiment_data_to_dataframe([data_row])

        # Check datetime columns are converted
        assert pd.api.types.is_datetime64_any_dtype(result["created_at"])
        assert pd.api.types.is_datetime64_any_dtype(result["updated_at"])

        # Check categorical columns for memory efficiency
        assert isinstance(result["participant_id"].dtype, pd.CategoricalDtype)
        assert isinstance(result["experiment_uuid"].dtype, pd.CategoricalDtype)

        # Check UUID converted to string
        assert isinstance(result.loc[0, "experiment_uuid"], str)

    def test_custom_data_flattening(self):
        """Test custom experiment data fields are properly flattened."""
        data_row = ExperimentDataRow(
            id=1,
            experiment_uuid=UUID("550e8400-e29b-41d4-a716-446655440000"),
            participant_id="PART-001",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            # Custom fields that should be flattened
            reaction_time=1.23,
            stimulus_type="visual",
            difficulty_level=2,
            correct=True,
        )

        result = experiment_data_to_dataframe([data_row])

        # All custom fields should be top-level columns
        assert "reaction_time" in result.columns
        assert "stimulus_type" in result.columns
        assert "difficulty_level" in result.columns
        assert "correct" in result.columns

        # Values should be preserved correctly
        assert result.loc[0, "reaction_time"] == 1.23
        assert result.loc[0, "stimulus_type"] == "visual"
        assert result.loc[0, "difficulty_level"] == 2
        assert result.loc[0, "correct"] == True
