"""Experiment types resource for WAVE client."""

from typing import Any, Dict, List, Optional

import pandas as pd
from wave_client.models.base import (
    ExperimentTypeCreate,
    ExperimentTypeUpdate,
)
from wave_client.resources.base import BaseResource


class ExperimentTypesResource(BaseResource):
    """Resource for managing experiment types."""

    async def create(
        self,
        name: str,
        table_name: str,
        schema_definition: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new experiment type.

        Args:
            name: Experiment type name (max 100 characters).
            table_name: Database table name (max 100 characters).
            schema_definition: Column definitions for experiment data.
            description: Experiment type description.

        Returns:
            Created experiment type response.
        """
        # Validate input data
        validated_data = ExperimentTypeCreate(
            name=name,
            table_name=table_name,
            schema_definition=schema_definition or {},
            description=description,
        )

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

    async def update(
        self,
        experiment_type_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        schema_definition: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Update experiment type.

        Args:
            experiment_type_id: Experiment type ID.
            name: Experiment type name (max 100 characters).
            description: Experiment type description.
            schema_definition: Column definitions.

        Returns:
            Updated experiment type response.
        """
        # Validate input data
        validated_data = ExperimentTypeUpdate(
            name=name,
            description=description,
            schema_definition=schema_definition,
        )

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
