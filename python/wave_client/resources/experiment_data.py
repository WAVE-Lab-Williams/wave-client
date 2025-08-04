"""Experiment data resource for WAVE client."""

from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd
from wave_client.models.base import (
    ExperimentDataCreate,
    ExperimentDataQuery,
    ExperimentDataRow,
    ExperimentDataUpdate,
)
from wave_client.resources.base import BaseResource


class ExperimentDataResource(BaseResource):
    """Resource for managing experiment data."""

    async def create(self, experiment_id: str, data_row: Dict[str, Any]) -> Dict[str, Any]:
        """Add new data row to experiment.

        Args:
            experiment_id: Experiment ID (UUID string).
            data_row: Data row creation data.

        Returns:
            Complete data row with all fields.
        """
        # Validate input data
        validated_data = ExperimentDataCreate(**data_row)

        return await self._request(
            "POST",
            f"/api/v1/experiment-data/{experiment_id}/data/",
            json_data=validated_data.model_dump(),
        )

    async def get_data(
        self,
        experiment_id: str,
        participant_id: Optional[str] = None,
        created_after: Optional[datetime] = None,
        created_before: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> pd.DataFrame:
        """Get experiment data as pandas DataFrame.

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
        data_rows = await self.get_data_raw(
            experiment_id, participant_id, created_after, created_before, limit, offset
        )

        if not data_rows:
            return pd.DataFrame()

        # Convert to ExperimentDataRow objects for proper handling
        data_row_objects = [ExperimentDataRow(**row) for row in data_rows]

        return self._to_dataframe(data_row_objects)

    async def get_data_raw(
        self,
        experiment_id: str,
        participant_id: Optional[str] = None,
        created_after: Optional[datetime] = None,
        created_before: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """Get experiment data as raw dictionary list.

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
        params = {"limit": limit, "offset": offset}

        if participant_id:
            params["participant_id"] = participant_id
        if created_after:
            params["created_after"] = created_after.isoformat()
        if created_before:
            params["created_before"] = created_before.isoformat()

        return await self._request(
            "GET", f"/api/v1/experiment-data/{experiment_id}/data/", params=params
        )

    async def count_data(
        self, experiment_id: str, participant_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Count data rows with filtering.

        Args:
            experiment_id: Experiment ID (UUID string).
            participant_id: Filter by participant ID.

        Returns:
            Count response.
        """
        params = {}
        if participant_id:
            params["participant_id"] = participant_id

        return await self._request(
            "GET", f"/api/v1/experiment-data/{experiment_id}/data/count", params=params
        )

    async def get_columns(self, experiment_id: str) -> Dict[str, Any]:
        """Get detailed column schema info.

        Args:
            experiment_id: Experiment ID (UUID string).

        Returns:
            List of column type information.
        """
        return await self._request("GET", f"/api/v1/experiment-data/{experiment_id}/data/columns")

    async def get_row(self, experiment_id: str, row_id: int) -> Dict[str, Any]:
        """Get specific data row by ID.

        Args:
            experiment_id: Experiment ID (UUID string).
            row_id: Data row ID.

        Returns:
            Complete row data.
        """
        return await self._request(
            "GET", f"/api/v1/experiment-data/{experiment_id}/data/row/{row_id}"
        )

    async def update_row(
        self, experiment_id: str, row_id: int, update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update specific data row.

        Args:
            experiment_id: Experiment ID (UUID string).
            row_id: Data row ID.
            update_data: Update data.

        Returns:
            Updated row data.
        """
        # Validate input data
        validated_data = ExperimentDataUpdate(**update_data)

        return await self._request(
            "PUT",
            f"/api/v1/experiment-data/{experiment_id}/data/row/{row_id}",
            json_data=validated_data.model_dump(exclude_none=True),
        )

    async def delete_row(self, experiment_id: str, row_id: int) -> Dict[str, Any]:
        """Delete specific data row.

        Args:
            experiment_id: Experiment ID (UUID string).
            row_id: Data row ID.

        Returns:
            Delete confirmation response.
        """
        return await self._request(
            "DELETE", f"/api/v1/experiment-data/{experiment_id}/data/row/{row_id}"
        )

    async def query_data(self, experiment_id: str, query_request: Dict[str, Any]) -> pd.DataFrame:
        """Advanced data querying with custom filters, returns DataFrame.

        Args:
            experiment_id: Experiment ID (UUID string).
            query_request: Query parameters.

        Returns:
            pandas DataFrame of matching rows.
        """
        data_rows = await self.query_data_raw(experiment_id, query_request)

        if not data_rows:
            return pd.DataFrame()

        # Convert to ExperimentDataRow objects for proper handling
        data_row_objects = [ExperimentDataRow(**row) for row in data_rows]

        return self._to_dataframe(data_row_objects)

    async def query_data_raw(
        self, experiment_id: str, query_request: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Advanced data querying with custom filters, returns raw data.

        Args:
            experiment_id: Experiment ID (UUID string).
            query_request: Query parameters.

        Returns:
            List of matching rows as dictionaries.
        """
        # Validate input data
        validated_query = ExperimentDataQuery(**query_request)

        return await self._request(
            "POST",
            f"/api/v1/experiment-data/{experiment_id}/data/query",
            json_data=validated_query.model_dump(),
        )

    # Batch operations

    async def create_batch(
        self, experiment_id: str, data_rows: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Create multiple data rows efficiently.

        Args:
            experiment_id: Experiment ID (UUID string).
            data_rows: List of data row creation data.

        Returns:
            List of created data rows.
        """
        results = []
        for data_row in data_rows:
            result = await self.create(experiment_id, data_row)
            results.append(result)
        return results

    async def get_all_data(self, experiment_id: str, batch_size: int = 1000) -> pd.DataFrame:
        """Get all experiment data with automatic pagination as DataFrame.

        Args:
            experiment_id: Experiment ID (UUID string).
            batch_size: Size of each batch.

        Returns:
            pandas DataFrame of all experiment data.
        """
        all_data = await self.get_all_data_raw(experiment_id, batch_size)

        if not all_data:
            return pd.DataFrame()

        # Convert to ExperimentDataRow objects for proper handling
        data_row_objects = [ExperimentDataRow(**row) for row in all_data]

        return self._to_dataframe(data_row_objects)

    async def get_all_data_raw(
        self, experiment_id: str, batch_size: int = 1000
    ) -> List[Dict[str, Any]]:
        """Get all experiment data with automatic pagination as raw data.

        Args:
            experiment_id: Experiment ID (UUID string).
            batch_size: Size of each batch.

        Returns:
            List of all experiment data rows as dictionaries.
        """
        all_data = []
        offset = 0

        while True:
            batch = await self.get_data_raw(
                experiment_id=experiment_id, limit=batch_size, offset=offset
            )

            if not batch:
                break

            all_data.extend(batch)

            if len(batch) < batch_size:
                break

            offset += batch_size

        return all_data
