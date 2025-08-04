"""Base resource class for WAVE client."""

from typing import TYPE_CHECKING, Any, Dict, List, Optional

import pandas as pd
from wave_client.models.base import ExperimentDataRow
from wave_client.utils.pandas_utils import experiment_data_to_dataframe

if TYPE_CHECKING:
    from wave_client.client import WaveClient


class BaseResource:
    """Base class for all WAVE API resources."""

    def __init__(self, client: "WaveClient"):
        """Initialize resource with client reference.

        Args:
            client: The main WaveClient instance.
        """
        self._client = client

    async def _request(
        self,
        method: str,
        url: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make HTTP request via client.

        Args:
            method: HTTP method.
            url: URL path.
            json_data: JSON request data.
            params: Query parameters.

        Returns:
            Response data.
        """
        return await self._client._http_client.request(method, url, json_data, params)

    def _to_dataframe(self, data_rows: List[ExperimentDataRow]) -> pd.DataFrame:
        """Convert experiment data rows to pandas DataFrame.

        Args:
            data_rows: List of experiment data rows.

        Returns:
            pandas DataFrame ready for analysis.
        """
        return experiment_data_to_dataframe(data_rows)
