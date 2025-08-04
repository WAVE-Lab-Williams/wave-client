"""Experiment types resource for WAVE client."""

from typing import Any, Dict, List

import pandas as pd
from wave_client.models.base import (
    ExperimentTypeCreate,
    ExperimentTypeUpdate,
)
from wave_client.resources.base import BaseResource


class ExperimentTypesResource(BaseResource):
    """Resource for managing experiment types."""

    async def create(self, experiment_type_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new experiment type.

        Args:
            experiment_type_data: Experiment type creation data.

        Returns:
            Created experiment type response.
        """
        # Validate input data
        validated_data = ExperimentTypeCreate(**experiment_type_data)

        return await self._request(
            "POST", "/api/v1/experiment-types/", json_data=validated_data.model_dump()
        )

    async def get(self, experiment_type_id: int) -> Dict[str, Any]:
        """Get experiment type by ID.

        Args:
            experiment_type_id: Experiment type ID.

        Returns:
            Experiment type response.
        """
        return await self._request("GET", f"/api/v1/experiment-types/{experiment_type_id}")

    async def list(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """List experiment types with pagination.

        Args:
            skip: Number of records to skip.
            limit: Maximum number of records to return.

        Returns:
            List of experiment type responses.
        """
        params = {"skip": skip, "limit": limit}
        return await self._request("GET", "/api/v1/experiment-types/", params=params)

    async def update(self, experiment_type_id: int, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update experiment type.

        Args:
            experiment_type_id: Experiment type ID.
            update_data: Update data.

        Returns:
            Updated experiment type response.
        """
        # Validate input data
        validated_data = ExperimentTypeUpdate(**update_data)

        return await self._request(
            "PUT",
            f"/api/v1/experiment-types/{experiment_type_id}",
            json_data=validated_data.model_dump(exclude_none=True),
        )

    async def delete(self, experiment_type_id: int) -> Dict[str, Any]:
        """Delete experiment type.

        Args:
            experiment_type_id: Experiment type ID.

        Returns:
            Delete confirmation response.
        """
        return await self._request("DELETE", f"/api/v1/experiment-types/{experiment_type_id}")

    async def get_columns_by_name(self, experiment_type_name: str) -> Dict[str, Any]:
        """Get schema information for experiment type by name.

        Args:
            experiment_type_name: Experiment type name.

        Returns:
            Experiment columns response.
        """
        return await self._request(
            "GET", f"/api/v1/experiment-types/name/{experiment_type_name}/columns"
        )

    # Pandas integration methods

    async def list_as_dataframe(self, **kwargs) -> pd.DataFrame:
        """List experiment types as pandas DataFrame.

        Args:
            **kwargs: Arguments passed to list().

        Returns:
            pandas DataFrame of experiment types.
        """
        data = await self.list(**kwargs)

        if not data:
            return pd.DataFrame()

        # Convert to DataFrame
        df = pd.DataFrame(data)

        # Type conversions - datetime columns
        datetime_cols = ["created_at", "updated_at"]
        for col in datetime_cols:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col])

        return df
