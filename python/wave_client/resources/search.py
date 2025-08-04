"""Search resource for WAVE client."""

from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd
from wave_client.models.base import ExperimentDataRow
from wave_client.models.search import (
    AdvancedExperimentSearchRequest,
    ExperimentDataByTagsRequest,
    ExperimentDescriptionSearchRequest,
    ExperimentTagSearchRequest,
    ExperimentTypeSearchRequest,
    TagSearchRequest,
)
from wave_client.resources.base import BaseResource


class SearchResource(BaseResource):
    """Resource for advanced search across all resources."""

    # Experiment search methods

    async def experiments_by_tags(
        self,
        tags: List[str],
        match_all: bool = True,
        created_after: Optional[datetime] = None,
        created_before: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> pd.DataFrame:
        """Find experiments by tag criteria.

        Args:
            tags: Tags to search for.
            match_all: Match ALL tags (True) or ANY tag (False).
            created_after: Filter by creation date (after).
            created_before: Filter by creation date (before).
            skip: Number of records to skip.
            limit: Maximum number of records to return.

        Returns:
            pandas DataFrame of matching experiments.
        """
        request_data = ExperimentTagSearchRequest(
            tags=tags,
            match_all=match_all,
            created_after=created_after,
            created_before=created_before,
            skip=skip,
            limit=limit,
        )

        response = await self._request(
            "POST",
            "/api/v1/search/experiments/by-tags",
            json_data=request_data.model_dump(exclude_none=True),
        )

        experiments = response.get("experiments", [])
        if not experiments:
            return pd.DataFrame()

        return self._experiments_to_dataframe(experiments)

    async def experiments_by_description_and_type(
        self,
        experiment_type_id: int,
        search_text: str,
        created_after: Optional[datetime] = None,
        created_before: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> pd.DataFrame:
        """Search experiment descriptions within specific type.

        Args:
            experiment_type_id: Experiment type ID.
            search_text: Text to search for.
            created_after: Filter by creation date (after).
            created_before: Filter by creation date (before).
            skip: Number of records to skip.
            limit: Maximum number of records to return.

        Returns:
            pandas DataFrame of matching experiments.
        """
        request_data = ExperimentDescriptionSearchRequest(
            experiment_type_id=experiment_type_id,
            search_text=search_text,
            created_after=created_after,
            created_before=created_before,
            skip=skip,
            limit=limit,
        )

        response = await self._request(
            "POST",
            "/api/v1/search/experiments/by-description-and-type",
            json_data=request_data.model_dump(exclude_none=True),
        )

        experiments = response.get("experiments", [])
        if not experiments:
            return pd.DataFrame()

        return self._experiments_to_dataframe(experiments)

    async def experiments_advanced(
        self,
        search_text: Optional[str] = None,
        tags: Optional[List[str]] = None,
        match_all_tags: bool = True,
        experiment_type_id: Optional[int] = None,
        created_after: Optional[datetime] = None,
        created_before: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> pd.DataFrame:
        """Advanced experiment search with multiple criteria.

        Args:
            search_text: Text search in descriptions.
            tags: Tag filters.
            match_all_tags: Match ALL tags (True) or ANY tag (False).
            experiment_type_id: Filter by experiment type.
            created_after: Filter by creation date (after).
            created_before: Filter by creation date (before).
            skip: Number of records to skip.
            limit: Maximum number of records to return.

        Returns:
            pandas DataFrame of matching experiments.
        """
        request_data = AdvancedExperimentSearchRequest(
            search_text=search_text,
            tags=tags,
            match_all_tags=match_all_tags,
            experiment_type_id=experiment_type_id,
            created_after=created_after,
            created_before=created_before,
            skip=skip,
            limit=limit,
        )

        response = await self._request(
            "POST",
            "/api/v1/search/experiments/advanced",
            json_data=request_data.model_dump(exclude_none=True),
        )

        experiments = response.get("experiments", [])
        if not experiments:
            return pd.DataFrame()

        return self._experiments_to_dataframe(experiments)

    # Experiment type search methods

    async def experiment_types_by_description(
        self,
        search_text: str,
        created_after: Optional[datetime] = None,
        created_before: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> pd.DataFrame:
        """Search experiment types by description.

        Args:
            search_text: Text to search for.
            created_after: Filter by creation date (after).
            created_before: Filter by creation date (before).
            skip: Number of records to skip.
            limit: Maximum number of records to return.

        Returns:
            pandas DataFrame of matching experiment types.
        """
        request_data = ExperimentTypeSearchRequest(
            search_text=search_text,
            created_after=created_after,
            created_before=created_before,
            skip=skip,
            limit=limit,
        )

        response = await self._request(
            "POST",
            "/api/v1/search/experiment-types/by-description",
            json_data=request_data.model_dump(exclude_none=True),
        )

        experiment_types = response.get("experiment_types", [])
        if not experiment_types:
            return pd.DataFrame()

        df = pd.DataFrame(experiment_types)

        # Type conversions - datetime columns
        datetime_cols = ["created_at", "updated_at"]
        for col in datetime_cols:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col])

        return df

    # Tag search methods

    async def tags_by_name(
        self,
        search_text: str,
        created_after: Optional[datetime] = None,
        created_before: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> pd.DataFrame:
        """Search tags by name/description.

        Args:
            search_text: Text to search for.
            created_after: Filter by creation date (after).
            created_before: Filter by creation date (before).
            skip: Number of records to skip.
            limit: Maximum number of records to return.

        Returns:
            pandas DataFrame of matching tags.
        """
        request_data = TagSearchRequest(
            search_text=search_text,
            created_after=created_after,
            created_before=created_before,
            skip=skip,
            limit=limit,
        )

        response = await self._request(
            "POST",
            "/api/v1/search/tags/by-name",
            json_data=request_data.model_dump(exclude_none=True),
        )

        tags = response.get("tags", [])
        if not tags:
            return pd.DataFrame()

        df = pd.DataFrame(tags)

        # Type conversions - datetime columns
        datetime_cols = ["created_at", "updated_at"]
        for col in datetime_cols:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col])

        return df

    # Experiment data search methods

    async def experiment_data_by_tags(
        self,
        tags: List[str],
        match_all: bool = True,
        created_after: Optional[datetime] = None,
        created_before: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 500,
    ) -> pd.DataFrame:
        """Get experiment data for experiments matching tags.

        Args:
            tags: Tags to search for.
            match_all: Match ALL tags (True) or ANY tag (False).
            created_after: Filter by creation date (after).
            created_before: Filter by creation date (before).
            skip: Number of records to skip.
            limit: Maximum data rows to return.

        Returns:
            pandas DataFrame of experiment data with metadata.
        """
        request_data = ExperimentDataByTagsRequest(
            tags=tags,
            match_all=match_all,
            created_after=created_after,
            created_before=created_before,
            skip=skip,
            limit=limit,
        )

        response = await self._request(
            "POST",
            "/api/v1/search/experiment-data/by-tags",
            json_data=request_data.model_dump(exclude_none=True),
        )

        data_rows = response.get("data", [])
        if not data_rows:
            return pd.DataFrame()

        # Convert to ExperimentDataRow objects for proper handling
        data_row_objects = [ExperimentDataRow(**row) for row in data_rows]

        return self._to_dataframe(data_row_objects)

    # Helper methods

    def _experiments_to_dataframe(self, experiments: List[Dict[str, Any]]) -> pd.DataFrame:
        """Convert experiments list to DataFrame with consistent formatting.

        Args:
            experiments: List of experiment dictionaries.

        Returns:
            pandas DataFrame of experiments.
        """
        records = []
        for exp in experiments:
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
