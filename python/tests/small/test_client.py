"""Unit tests for the main WaveClient class."""

from unittest.mock import patch

import pytest
from wave_client import WaveClient
from wave_client.resources import (
    ExperimentDataResource,
    ExperimentsResource,
    ExperimentTypesResource,
    SearchResource,
    TagsResource,
)


class TestWaveClientInitialization:
    """Test WaveClient initialization and configuration."""

    def test_client_initialization_with_defaults(self):
        """Test client initializes with default configuration."""
        client = WaveClient(api_key="test-key")

        assert client.experiment_types is not None
        assert isinstance(client.experiment_types, ExperimentTypesResource)
        assert isinstance(client.tags, TagsResource)
        assert isinstance(client.experiments, ExperimentsResource)
        assert isinstance(client.experiment_data, ExperimentDataResource)
        assert isinstance(client.search, SearchResource)

    def test_client_initialization_with_custom_config(self):
        """Test client initializes with custom configuration."""
        client = WaveClient(
            api_key="custom-key", base_url="https://custom-api.com", max_retries=5, timeout=60.0
        )

        # Check that HTTP client was configured (we can't easily test the internals)
        assert client._http_client is not None

    @patch.dict("os.environ", {"WAVE_API_KEY": "env-api-key"})
    def test_client_uses_environment_variables(self):
        """Test client picks up API key from environment."""
        client = WaveClient()  # No explicit api_key

        # Client should initialize without error when env var is set
        assert client._http_client is not None


class TestWaveClientContextManager:
    """Test WaveClient async context manager functionality."""

    @pytest.mark.asyncio
    async def test_context_manager_lifecycle(self, mock_http_client):
        """Test client context manager enter/exit lifecycle."""
        client = WaveClient(api_key="test-key")
        client._http_client = mock_http_client

        # Test async context manager
        async with client as ctx_client:
            assert ctx_client is client

        # Verify HTTP client lifecycle was called
        mock_http_client.__aenter__.assert_called_once()
        mock_http_client.__aexit__.assert_called_once()

    @pytest.mark.asyncio
    async def test_manual_close(self, mock_http_client):
        """Test manual client close."""
        client = WaveClient(api_key="test-key")
        client._http_client = mock_http_client

        await client.close()

        mock_http_client.close.assert_called_once()


class TestWaveClientUtilityMethods:
    """Test WaveClient utility methods."""

    @pytest.mark.asyncio
    async def test_get_health(self, wave_client, mock_http_client):
        """Test health check method."""
        expected_response = {"status": "healthy", "service": "wave-backend"}
        mock_http_client.request.return_value = expected_response

        result = await wave_client.get_health()

        assert result == expected_response
        mock_http_client.request.assert_called_once_with("GET", "/health")

    @pytest.mark.asyncio
    async def test_get_version(self, wave_client, mock_http_client):
        """Test version info method."""
        expected_response = {"api_version": "1.0.0", "client_version": "1.0.0", "compatible": True}
        mock_http_client.request.return_value = expected_response

        result = await wave_client.get_version()

        assert result == expected_response
        mock_http_client.request.assert_called_once_with("GET", "/version")

    def test_to_dataframe_utility(self, wave_client, sample_experiment_data_rows):
        """Test DataFrame conversion utility method."""
        from wave_client.models.base import ExperimentDataRow

        # Convert raw data to ExperimentDataRow objects
        data_row_objects = [ExperimentDataRow(**row) for row in sample_experiment_data_rows]

        df = wave_client.to_dataframe(data_row_objects)

        assert not df.empty
        assert len(df) == 2
        assert "participant_id" in df.columns
        assert "reaction_time" in df.columns
