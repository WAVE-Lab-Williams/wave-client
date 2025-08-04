"""Integration tests for WAVE client against live backend."""

import pandas as pd
import pytest
from wave_client.exceptions import NotFoundError


class TestBasicConnectivity:
    """Test basic connection and health checks."""

    @pytest.mark.asyncio
    async def test_health_check(self, integration_client):
        """Test health endpoint connectivity."""
        health = await integration_client.get_health()

        assert "status" in health
        assert health["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_version_check(self, integration_client):
        """Test version endpoint and compatibility."""
        version_info = await integration_client.get_version()

        assert "api_version" in version_info
        assert "client_version" in version_info
        # Should have compatibility info
        assert "compatible" in version_info


class TestExperimentTypesIntegration:
    """Test experiment types CRUD operations."""

    @pytest.mark.asyncio
    async def test_experiment_type_lifecycle(self, integration_client, sample_experiment_type_data):
        """Test complete experiment type lifecycle: create, read, update, delete."""
        # Create
        created = await integration_client.experiment_types.create(sample_experiment_type_data)
        assert "id" in created
        exp_type_id = created["id"]

        try:
            # Read
            retrieved = await integration_client.experiment_types.get(exp_type_id)
            assert retrieved["name"] == sample_experiment_type_data["name"]
            assert retrieved["table_name"] == sample_experiment_type_data["table_name"]

            # Update
            update_data = {"description": "Updated integration test description"}
            updated = await integration_client.experiment_types.update(exp_type_id, update_data)
            assert updated["description"] == update_data["description"]

            # List as DataFrame
            df = await integration_client.experiment_types.list_as_dataframe()
            assert not df.empty
            assert exp_type_id in df["id"].values

        finally:
            # Cleanup - delete
            await integration_client.experiment_types.delete(exp_type_id)

            # Verify deletion
            with pytest.raises(NotFoundError):
                await integration_client.experiment_types.get(exp_type_id)


class TestExperimentsIntegration:
    """Test experiments CRUD operations."""

    @pytest.mark.asyncio
    async def test_experiment_lifecycle_with_data(
        self,
        integration_client,
        sample_experiment_type_data,
        sample_experiment_data,
        sample_experiment_data_rows,
    ):
        """Test complete experiment workflow with data logging."""
        # First create experiment type
        exp_type = await integration_client.experiment_types.create(sample_experiment_type_data)
        exp_type_id = exp_type["id"]

        try:
            # Create experiment
            experiment_data = {**sample_experiment_data, "experiment_type_id": exp_type_id}
            created_exp = await integration_client.experiments.create(experiment_data)
            exp_uuid = created_exp["uuid"]

            try:
                # Add experiment data
                for data_row in sample_experiment_data_rows:
                    # Structure data according to ExperimentDataCreate model
                    participant_id = data_row.pop("participant_id")
                    formatted_data = {
                        "participant_id": participant_id,
                        "data": data_row,  # All other fields go into 'data'
                    }
                    await integration_client.experiment_data.create(exp_uuid, formatted_data)

                # Retrieve data as DataFrame
                df = await integration_client.experiment_data.get_data(exp_uuid)

                # Verify DataFrame structure and content
                assert not df.empty
                assert len(df) == len(sample_experiment_data_rows)
                assert "participant_id" in df.columns
                assert "reaction_time" in df.columns
                assert "accuracy" in df.columns

                # Check data types
                assert pd.api.types.is_datetime64_any_dtype(df["created_at"])
                assert isinstance(df["participant_id"].dtype, pd.CategoricalDtype)

                # Verify data values
                participants = df["participant_id"].unique()
                assert "INT_TEST_001" in participants
                assert "INT_TEST_002" in participants

                # Test data filtering
                filtered_df = await integration_client.experiment_data.get_data(
                    exp_uuid, participant_id="INT_TEST_001"
                )
                assert len(filtered_df) == 2  # Two rows for this participant

            finally:
                # Cleanup experiment
                await integration_client.experiments.delete(exp_uuid)

        finally:
            # Cleanup experiment type
            await integration_client.experiment_types.delete(exp_type_id)


class TestTagsIntegration:
    """Test tags CRUD operations."""

    @pytest.mark.asyncio
    async def test_tags_lifecycle(self, integration_client, sample_tag_data):
        """Test complete tags lifecycle."""
        # Create
        created = await integration_client.tags.create(sample_tag_data)
        tag_id = created["id"]

        try:
            # Read
            retrieved = await integration_client.tags.get(tag_id)
            assert retrieved["name"] == sample_tag_data["name"]

            # List as DataFrame
            df = await integration_client.tags.list_as_dataframe()
            assert not df.empty
            assert tag_id in df["id"].values

            # Update
            update_data = {"description": "Updated integration test tag"}
            updated = await integration_client.tags.update(tag_id, update_data)
            assert updated["description"] == update_data["description"]

        finally:
            # Cleanup
            await integration_client.tags.delete(tag_id)


class TestSearchIntegration:
    """Test search functionality."""

    @pytest.mark.asyncio
    async def test_search_experiments_by_tags(
        self, integration_client, sample_experiment_type_data, sample_experiment_data
    ):
        """Test searching experiments by tags."""
        # Create experiment type
        exp_type = await integration_client.experiment_types.create(sample_experiment_type_data)
        exp_type_id = exp_type["id"]

        # Create tags for testing
        import uuid

        unique_id = str(uuid.uuid4())[:8]
        tag1 = await integration_client.tags.create(
            {"name": f"integration_test_{unique_id}", "description": "Tag for integration test"}
        )
        tag2 = await integration_client.tags.create(
            {"name": f"search_test_{unique_id}", "description": "Tag for search test"}
        )

        try:
            # Create experiment with specific tags
            experiment_data = {
                **sample_experiment_data,
                "experiment_type_id": exp_type_id,
                "tags": [tag1["name"], tag2["name"]],
            }
            created_exp = await integration_client.experiments.create(experiment_data)
            exp_uuid = created_exp["uuid"]

            try:
                # Search by tags
                search_results = await integration_client.search.experiments_by_tags(
                    tags=[tag1["name"]], match_all=False
                )

                # Should return DataFrame
                assert isinstance(search_results, pd.DataFrame)

                # Should find our experiment
                if not search_results.empty:
                    uuids = search_results["uuid"].astype(str).values
                    assert exp_uuid in uuids

            finally:
                # Cleanup experiment
                await integration_client.experiments.delete(exp_uuid)

        finally:
            # Cleanup experiment type
            await integration_client.experiment_types.delete(exp_type_id)
            # Cleanup tags
            await integration_client.tags.delete(tag1["id"])
            await integration_client.tags.delete(tag2["id"])


class TestDataFrameConversions:
    """Test pandas DataFrame conversions and data types."""

    @pytest.mark.asyncio
    async def test_dataframe_utility_method(self, integration_client, sample_experiment_data_rows):
        """Test the utility DataFrame conversion method."""
        from datetime import datetime
        from uuid import UUID

        from wave_client.models.base import ExperimentDataRow

        # Create ExperimentDataRow objects
        data_rows = []
        for i, row_data in enumerate(sample_experiment_data_rows):
            data_row = ExperimentDataRow(
                id=i + 1,
                experiment_uuid=UUID("550e8400-e29b-41d4-a716-446655440000"),
                created_at=datetime.now(),
                updated_at=datetime.now(),
                **row_data,
            )
            data_rows.append(data_row)

        # Convert using client utility
        df = integration_client.to_dataframe(data_rows)

        # Verify DataFrame structure
        assert not df.empty
        assert len(df) == len(sample_experiment_data_rows)

        # Check required columns
        required_cols = ["id", "experiment_uuid", "participant_id", "created_at", "updated_at"]
        for col in required_cols:
            assert col in df.columns

        # Check custom data columns
        assert "reaction_time" in df.columns
        assert "accuracy" in df.columns
        assert "stimulus_type" in df.columns

        # Check data types
        assert pd.api.types.is_datetime64_any_dtype(df["created_at"])
        assert isinstance(df["participant_id"].dtype, pd.CategoricalDtype)
