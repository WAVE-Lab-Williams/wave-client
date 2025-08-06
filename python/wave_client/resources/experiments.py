"""Experiments resource for WAVE client."""

from typing import Any, Dict, List, Optional

import pandas as pd
from wave_client.models.base import ExperimentCreate, ExperimentUpdate
from wave_client.resources.base import BaseResource


class ExperimentsResource(BaseResource):
    """Resource for managing experiments."""

    async def create(
        self,
        experiment_type_id: int,
        description: str,
        tags: Optional[List[str]] = None,
        additional_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create a new experiment.

        Args:
            experiment_type_id: Experiment type ID (must be > 0).
            description: Experiment description.
            tags: List of tags (max 10).
            additional_data: Additional metadata.

        Returns:
            Created experiment response.
        """
        # Validate input data
        validated_data = ExperimentCreate(
            experiment_type_id=experiment_type_id,
            description=description,
            tags=tags or [],
            additional_data=additional_data or {},
        )

        return await self._request(
            "POST", "/api/v1/experiments/", json_data=validated_data.model_dump()
        )

    async def get(self, experiment_uuid: str) -> Dict[str, Any]:
        """Get experiment by UUID.

        Args:
            experiment_uuid: Experiment UUID.

        Returns:
            Experiment response.
        """
        return await self._request("GET", f"/api/v1/experiments/{experiment_uuid}")

    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        experiment_type_id: Optional[int] = None,
        tags: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """List experiments with filtering.

        Args:
            skip: Number of records to skip.
            limit: Maximum number of records to return.
            experiment_type_id: Filter by experiment type ID.
            tags: Filter by tags.

        Returns:
            List of experiment responses.
        """
        params = {"skip": skip, "limit": limit}

        if experiment_type_id is not None:
            params["experiment_type_id"] = experiment_type_id

        if tags:
            # Handle multiple tags in query params
            for tag in tags:
                if "tags" not in params:
                    params["tags"] = []
                if isinstance(params["tags"], list):
                    params["tags"].append(tag)
                else:
                    params["tags"] = [params["tags"], tag]

        return await self._request("GET", "/api/v1/experiments/", params=params)

    async def update(
        self,
        experiment_uuid: str,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        additional_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Update experiment.

        Args:
            experiment_uuid: Experiment UUID.
            description: Experiment description.
            tags: List of tags (max 10).
            additional_data: Additional metadata.

        Returns:
            Updated experiment response.
        """
        # Validate input data
        validated_data = ExperimentUpdate(
            description=description,
            tags=tags,
            additional_data=additional_data,
        )

        return await self._request(
            "PUT",
            f"/api/v1/experiments/{experiment_uuid}",
            json_data=validated_data.model_dump(exclude_none=True),
        )

    async def delete(self, experiment_uuid: str) -> Dict[str, Any]:
        """Delete experiment (requires ADMIN role).

        Args:
            experiment_uuid: Experiment UUID.

        Returns:
            Delete confirmation response.
        """
        return await self._request("DELETE", f"/api/v1/experiments/{experiment_uuid}")

    async def get_columns(self, experiment_uuid: str) -> Dict[str, Any]:
        """Get data schema information for experiment.

        Args:
            experiment_uuid: Experiment UUID.

        Returns:
            Experiment columns response.
        """
        return await self._request("GET", f"/api/v1/experiments/{experiment_uuid}/columns")

    # Convenience methods

    async def get_by_tags(
        self, tags: List[str], match_all: bool = True, **kwargs
    ) -> List[Dict[str, Any]]:
        """Filter experiments by tags.

        Args:
            tags: List of tags to filter by.
            match_all: Whether to match all tags (True) or any tag (False).
            **kwargs: Additional arguments passed to list().

        Returns:
            List of matching experiments.
        """
        # For now, use simple tag filtering via list method
        # More advanced tag matching can be implemented via search resource
        return await self.list(tags=tags, **kwargs)

    async def get_by_type(self, experiment_type_id: int, **kwargs) -> List[Dict[str, Any]]:
        """Filter experiments by type.

        Args:
            experiment_type_id: Experiment type ID.
            **kwargs: Additional arguments passed to list().

        Returns:
            List of matching experiments.
        """
        return await self.list(experiment_type_id=experiment_type_id, **kwargs)

    # Pandas integration methods

    async def list_as_dataframe(self, **kwargs) -> pd.DataFrame:
        """List experiments as pandas DataFrame.

        Args:
            **kwargs: Arguments passed to list().

        Returns:
            pandas DataFrame of experiments.
        """
        data = await self.list(**kwargs)

        if not data:
            return pd.DataFrame()

        # Convert to DataFrame - need to handle nested experiment_type
        records = []
        for exp in data:
            record = exp.copy()

            # Flatten experiment_type if present
            if "experiment_type" in record and record["experiment_type"]:
                exp_type = record.pop("experiment_type")
                # Add experiment type fields with prefix
                for key, value in exp_type.items():
                    record[f"type_{key}"] = value

            records.append(record)

        df = pd.DataFrame(records)

        # Type conversions - datetime columns
        datetime_cols = ["created_at", "updated_at", "type_created_at", "type_updated_at"]
        for col in datetime_cols:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col])

        # Convert UUID to string
        if "uuid" in df.columns:
            df["uuid"] = df["uuid"].astype(str)

        return df
