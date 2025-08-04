"""Search request models for WAVE client."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class ExperimentTagSearchRequest(BaseModel):
    """Search experiments by tags."""

    tags: List[str] = Field(..., min_length=1, description="Tags to search for")
    match_all: bool = Field(True, description="Match ALL tags (True) or ANY tag (False)")
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=1000)


class ExperimentTypeSearchRequest(BaseModel):
    """Search experiment types by description."""

    search_text: str = Field(..., min_length=1, description="Text to search for")
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=1000)


class TagSearchRequest(BaseModel):
    """Search tags by name/description."""

    search_text: str = Field(..., min_length=1, description="Text to search for")
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=1000)


class ExperimentDescriptionSearchRequest(BaseModel):
    """Search experiment descriptions within specific type."""

    experiment_type_id: int = Field(..., gt=0, description="Experiment type ID")
    search_text: str = Field(..., min_length=1, description="Text to search for")
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=1000)


class AdvancedExperimentSearchRequest(BaseModel):
    """Advanced experiment search with multiple criteria."""

    search_text: Optional[str] = Field(None, description="Text search in descriptions")
    tags: Optional[List[str]] = Field(None, description="Tag filters")
    match_all_tags: bool = Field(True, description="Match ALL tags (True) or ANY tag (False)")
    experiment_type_id: Optional[int] = Field(None, description="Filter by experiment type")
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=1000)


class ExperimentDataByTagsRequest(BaseModel):
    """Get experiment data for experiments matching tags."""

    tags: List[str] = Field(..., min_length=1, description="Tags to search for")
    match_all: bool = Field(True, description="Match ALL tags (True) or ANY tag (False)")
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    skip: int = Field(0, ge=0)
    limit: int = Field(500, ge=1, le=1000, description="Max data rows to return")
