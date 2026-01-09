"""Test configuration and shared fixtures for small (unit) tests."""

import json
from typing import Any, Dict
from unittest.mock import AsyncMock, MagicMock

import pandas as pd
import pytest
from wave_client import WaveClient
from wave_client.utils.http_client import HTTPClient


@pytest.fixture
def mock_http_response():
    """Create a mock HTTP response."""

    def _create_response(
        data: Dict[str, Any], status_code: int = 200, headers: Dict[str, str] = None
    ):
        response = MagicMock()
        response.status_code = status_code
        response.json.return_value = data
        response.text = json.dumps(data)
        default_headers = {"content-type": "application/json", "X-WAVE-API-Version": "1.0.0"}
        if headers:
            default_headers.update(headers)
        response.headers = default_headers
        return response

    return _create_response


@pytest.fixture
def mock_http_client(mock_http_response):
    """Create a mock HTTP client."""
    client = AsyncMock(spec=HTTPClient)

    # Configure default successful responses
    client.request = AsyncMock()

    return client


@pytest.fixture
async def wave_client(mock_http_client):
    """Create a WAVE client with mocked HTTP client."""
    client = WaveClient(api_key="test-api-key", base_url="http://localhost:8000")
    client._http_client = mock_http_client
    return client


@pytest.fixture
def sample_experiment_type():
    """Sample experiment type data."""
    return {
        "id": 1,
        "name": "reaction_time_test",
        "description": "Reaction time measurement experiment",
        "table_name": "rt_data",
        "schema_definition": {
            "reaction_time": "FLOAT",
            "accuracy": "FLOAT",
            "stimulus_type": "STRING",
        },
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T10:30:00Z",
    }


@pytest.fixture
def sample_experiment():
    """Sample experiment data."""
    return {
        "uuid": "550e8400-e29b-41d4-a716-446655440000",
        "experiment_type_id": 1,
        "description": "Visual reaction time study",
        "tags": ["reaction_time", "visual"],
        "additional_data": {"session_duration": 30},
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T10:30:00Z",
        "experiment_type": {
            "id": 1,
            "name": "reaction_time_test",
            "table_name": "rt_data",
            "schema_definition": {"reaction_time": "FLOAT", "accuracy": "FLOAT"},
        },
    }


@pytest.fixture
def sample_experiment_data_rows():
    """Sample experiment data rows."""
    return [
        {
            "id": 1,
            "experiment_uuid": "550e8400-e29b-41d4-a716-446655440000",
            "participant_id": "PART-001",
            "created_at": "2024-01-15T10:30:00Z",
            "updated_at": "2024-01-15T10:30:00Z",
            "reaction_time": 1.23,
            "accuracy": 0.95,
            "stimulus_type": "visual",
        },
        {
            "id": 2,
            "experiment_uuid": "550e8400-e29b-41d4-a716-446655440000",
            "participant_id": "PART-001",
            "created_at": "2024-01-15T10:31:00Z",
            "updated_at": "2024-01-15T10:31:00Z",
            "reaction_time": 0.87,
            "accuracy": 0.90,
            "stimulus_type": "auditory",
        },
    ]


@pytest.fixture
def sample_tag():
    """Sample tag data."""
    return {
        "id": 1,
        "name": "cognitive",
        "description": "Cognitive performance experiments",
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T10:30:00Z",
    }


@pytest.fixture
def sample_search_response():
    """Sample search response data."""
    return {
        "experiments": [
            {
                "uuid": "550e8400-e29b-41d4-a716-446655440000",
                "experiment_type_id": 1,
                "description": "Memory study",
                "tags": ["memory", "cognitive"],
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z",
            }
        ],
        "total": 1,
        "pagination": {"skip": 0, "limit": 100, "total": 1},
    }


@pytest.fixture
def assert_dataframe_structure():
    """Helper to assert DataFrame structure and types."""

    def _assert_structure(df: pd.DataFrame, expected_columns: list, expected_types: dict = None):
        # Check DataFrame is not empty
        assert not df.empty, "DataFrame should not be empty"

        # Check expected columns exist
        for col in expected_columns:
            assert col in df.columns, f"Column '{col}' should exist in DataFrame"

        # Check data types if provided
        if expected_types:
            for col, expected_type in expected_types.items():
                if col in df.columns:
                    actual_type = df[col].dtype
                    if expected_type == "datetime":
                        assert pd.api.types.is_datetime64_any_dtype(
                            actual_type
                        ), f"Column '{col}' should be datetime type, got {actual_type}"
                    elif expected_type == "category":
                        assert isinstance(
                            actual_type, pd.CategoricalDtype
                        ), f"Column '{col}' should be categorical type, got {actual_type}"

    return _assert_structure
