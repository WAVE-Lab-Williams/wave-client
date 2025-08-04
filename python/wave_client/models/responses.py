"""Response models for WAVE client."""

from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field
from wave_client.models.base import Experiment, ExperimentDataRow, ExperimentType, Tag


class PaginationInfo(BaseModel):
    """Pagination information for list responses."""

    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=1000)
    total: int = Field(0, ge=0)


class ExperimentSearchResponse(BaseModel):
    """Response for experiment search operations."""

    experiments: List[Experiment]
    total: int = Field(0, ge=0)
    pagination: PaginationInfo


class ExperimentTypeSearchResponse(BaseModel):
    """Response for experiment type search operations."""

    experiment_types: List[ExperimentType]
    total: int = Field(0, ge=0)
    pagination: PaginationInfo


class TagSearchResponse(BaseModel):
    """Response for tag search operations."""

    tags: List[Tag]
    total: int = Field(0, ge=0)
    pagination: PaginationInfo


class ExperimentDataByTagsResponse(BaseModel):
    """Response for experiment data search by tags."""

    data: List[ExperimentDataRow]
    total_rows: int = Field(0, ge=0, description="Total data rows returned")
    total_experiments: int = Field(0, ge=0, description="Total experiments matched")
    experiment_info: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict, description="Metadata per experiment UUID"
    )
    pagination: PaginationInfo


class ExperimentDataCountResponse(BaseModel):
    """Response for experiment data count operations."""

    count: int = Field(0, ge=0)
    participant_id: Optional[str] = None
    experiment_id: UUID


class ExperimentDataDeleteResponse(BaseModel):
    """Response for experiment data deletion."""

    message: str
    deleted_id: int
    experiment_id: UUID


class StandardDeleteResponse(BaseModel):
    """Standard response for delete operations."""

    message: str


class VersionResponse(BaseModel):
    """API version and compatibility information."""

    api_version: str
    client_version: Optional[str] = None
    compatible: Optional[bool] = None
    compatibility_rule: str
    warning: Optional[str] = None


class ColumnTypeInfo(BaseModel):
    """Information about a database column."""

    column_name: str
    column_type: str  # PostgreSQL type name
    is_nullable: bool
    default_value: Optional[Any] = None


class ExperimentColumns(BaseModel):
    """Schema information for an experiment."""

    columns: List[ColumnTypeInfo]
    experiment_uuid: Optional[UUID] = None
    experiment_type: Optional[str] = None
