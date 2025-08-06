"""Tags resource for WAVE client."""

from typing import Any, Dict, List, Optional

import pandas as pd
from wave_client.models.base import TagCreate, TagUpdate
from wave_client.resources.base import BaseResource


class TagsResource(BaseResource):
    """Resource for managing tags."""

    async def create(
        self,
        name: str,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new tag.

        Args:
            name: Tag name (max 100 characters).
            description: Tag description.

        Returns:
            Created tag response.
        """
        # Validate input data directly from parameters
        validated_data = TagCreate(name=name, description=description)

        return await self._request("POST", "/api/v1/tags/", json_data=validated_data.model_dump())

    async def get(self, tag_id: int) -> Dict[str, Any]:
        """Get tag by ID.

        Args:
            tag_id: Tag ID.

        Returns:
            Tag response.
        """
        return await self._request("GET", f"/api/v1/tags/{tag_id}")

    async def list(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """List tags with pagination.

        Args:
            skip: Number of records to skip.
            limit: Maximum number of records to return.

        Returns:
            List of tag responses.
        """
        params = {"skip": skip, "limit": limit}
        return await self._request("GET", "/api/v1/tags/", params=params)

    async def update(
        self,
        tag_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update tag.

        Args:
            tag_id: Tag ID.
            name: Tag name (max 100 characters).
            description: Tag description.

        Returns:
            Updated tag response.
        """
        # Validate input data directly from parameters
        validated_data = TagUpdate(name=name, description=description)

        return await self._request(
            "PUT", f"/api/v1/tags/{tag_id}", json_data=validated_data.model_dump(exclude_none=True)
        )

    async def delete(self, tag_id: int) -> Dict[str, Any]:
        """Delete tag.

        Args:
            tag_id: Tag ID.

        Returns:
            Delete confirmation response.
        """
        return await self._request("DELETE", f"/api/v1/tags/{tag_id}")

    # Pandas integration methods

    async def list_as_dataframe(self, **kwargs) -> pd.DataFrame:
        """List tags as pandas DataFrame.

        Args:
            **kwargs: Arguments passed to list().

        Returns:
            pandas DataFrame of tags.
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
