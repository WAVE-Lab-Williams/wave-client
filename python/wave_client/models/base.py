"""Core Pydantic models for WAVE client."""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

# Column definition can be simple string or complex object
ColumnDefinition = Union[str, Dict[str, Any]]


class TagCreate(BaseModel):
    """Data for creating a new tag."""

    name: str = Field(..., max_length=100, description="Tag name")
    description: Optional[str] = Field(None, description="Tag description")


class TagUpdate(BaseModel):
    """Data for updating an existing tag."""

    name: Optional[str] = Field(None, max_length=100, description="Tag name")
    description: Optional[str] = Field(None, description="Tag description")


class Tag(BaseModel):
    """Tag response from server."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ExperimentTypeCreate(BaseModel):
    """Data for creating a new experiment type."""

    name: str = Field(..., max_length=100, description="Experiment type name")
    table_name: str = Field(..., max_length=100, description="Database table name")
    schema_definition: Dict[str, ColumnDefinition] = Field(
        default_factory=dict, description="Column definitions for experiment data"
    )
    description: Optional[str] = Field(None, description="Experiment type description")

    @field_validator("schema_definition")
    def validate_schema_definition(cls, v):  # pylint: disable=no-self-argument
        """Validate schema definition follows backend rules."""
        reserved_names = {"id", "experiment_uuid", "participant_id", "created_at", "updated_at"}
        supported_types = {"INTEGER", "FLOAT", "STRING", "TEXT", "BOOLEAN", "DATETIME", "JSON"}

        for column_name, column_def in v.items():
            if column_name.lower() in reserved_names:
                raise ValueError(f"Column name '{column_name}' is reserved")

            if isinstance(column_def, str):
                if column_def.upper() not in supported_types:
                    raise ValueError(f"Unsupported column type: {column_def}")
            elif isinstance(column_def, dict):
                if "type" not in column_def:
                    raise ValueError(f"Column definition for '{column_name}' must include 'type'")
                if column_def["type"].upper() not in supported_types:
                    raise ValueError(f"Unsupported column type: {column_def['type']}")
        return v


class ExperimentTypeUpdate(BaseModel):
    """Data for updating an existing experiment type."""

    name: Optional[str] = Field(None, max_length=100, description="Experiment type name")
    description: Optional[str] = Field(None, description="Experiment type description")
    schema_definition: Optional[Dict[str, Any]] = Field(None, description="Column definitions")


class ExperimentType(BaseModel):
    """Experiment type response from server."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    table_name: str
    schema_definition: Dict[str, Any]
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ExperimentCreate(BaseModel):
    """Data for creating a new experiment."""

    experiment_type_id: int = Field(..., gt=0, description="Experiment type ID")
    description: str = Field(..., description="Experiment description")
    tags: List[str] = Field(default_factory=list, max_length=10, description="Tags (max 10)")
    additional_data: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class ExperimentUpdate(BaseModel):
    """Data for updating an existing experiment."""

    description: Optional[str] = Field(None, description="Experiment description")
    tags: Optional[List[str]] = Field(None, max_length=10, description="Tags (max 10)")
    additional_data: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class Experiment(BaseModel):
    """Experiment response from server."""

    model_config = ConfigDict(from_attributes=True)

    uuid: UUID
    experiment_type_id: int
    description: str
    tags: List[str] = Field(default_factory=list)
    additional_data: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime
    experiment_type: ExperimentType  # Nested model


class ExperimentDataCreate(BaseModel):
    """Data for creating an experiment data row."""

    participant_id: str = Field(..., max_length=100, description="Participant identifier")
    data: Dict[str, Any] = Field(..., description="Experiment data matching type schema")


class ExperimentDataUpdate(BaseModel):
    """Data for updating an experiment data row."""

    participant_id: Optional[str] = Field(
        None, max_length=100, description="Participant identifier"
    )
    data: Optional[Dict[str, Any]] = Field(None, description="Experiment data updates")


class ExperimentDataRow(BaseModel):
    """Experiment data row response with dynamic schema."""

    model_config = ConfigDict(
        from_attributes=True, extra="allow"  # Allow additional fields from dynamic schema
    )

    id: int
    experiment_uuid: UUID
    participant_id: str
    created_at: datetime
    updated_at: datetime
    # Additional fields will be added dynamically based on experiment type schema

    def get_custom_data(self) -> Dict[str, Any]:
        """Extract custom data fields (excluding standard columns)."""
        standard_fields = {"id", "experiment_uuid", "participant_id", "created_at", "updated_at"}
        return {k: v for k, v in self.model_dump().items() if k not in standard_fields}


class ExperimentDataQuery(BaseModel):
    """Query parameters for experiment data."""

    participant_id: Optional[str] = Field(None, max_length=100, description="Filter by participant")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Custom field filters")
    created_after: Optional[datetime] = Field(None, description="Filter by creation date (after)")
    created_before: Optional[datetime] = Field(None, description="Filter by creation date (before)")
    limit: int = Field(100, ge=1, le=1000, description="Maximum rows to return")
    offset: int = Field(0, ge=0, description="Number of rows to skip")
