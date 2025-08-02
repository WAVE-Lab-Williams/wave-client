# Core Data Types and Models

This document defines the core data types used across both JavaScript and Python WAVE clients, based on the backend data models.

## JavaScript Data Types (Plain Objects)

The JavaScript client uses plain JavaScript objects with consistent property naming.

### Tag
```javascript
// Tag creation data
const tagCreate = {
  name: "cognitive",                    // string, required, max 100 chars
  description: "Cognitive experiments"  // string, optional
};

// Tag response from server
const tag = {
  id: 1,                               // number, auto-generated
  name: "cognitive",                   // string
  description: "Cognitive experiments", // string or null
  created_at: "2024-01-15T10:30:00Z",  // ISO date string
  updated_at: "2024-01-15T10:30:00Z"   // ISO date string
};

// Tag update data (partial)
const tagUpdate = {
  name: "updated_cognitive",           // string, optional
  description: "Updated description"   // string, optional
};
```

### Experiment Type
```javascript
// Experiment type creation data
const experimentTypeCreate = {
  name: "cognitive_assessment",        // string, required, max 100 chars, unique
  description: "Cognitive evaluation", // string, optional
  table_name: "cognitive_test_data",   // string, required, max 100 chars, unique
  schema_definition: {                 // object, defines custom columns
    reaction_time: "FLOAT",            // simple column definition
    accuracy: "FLOAT",
    difficulty_level: "INTEGER",
    stimulus_type: "STRING",
    notes: {                          // complex column definition
      type: "TEXT",
      nullable: true
    }
  }
};

// Experiment type response from server
const experimentType = {
  id: 1,                               // number, auto-generated
  name: "cognitive_assessment",        // string
  description: "Cognitive evaluation", // string or null
  table_name: "cognitive_test_data",   // string
  schema_definition: {                 // object, column definitions
    reaction_time: "FLOAT",
    accuracy: "FLOAT",
    difficulty_level: "INTEGER",
    stimulus_type: "STRING"
  },
  created_at: "2024-01-15T10:30:00Z",  // ISO date string
  updated_at: "2024-01-15T10:30:00Z"   // ISO date string
};
```

### Experiment
```javascript
// Experiment creation data
const experimentCreate = {
  experiment_type_id: 1,               // number, required, must reference existing type
  description: "Visual stimuli test",  // string, required
  tags: ["cognitive", "visual"],       // array of strings, max 10 items
  additional_data: {                   // object, flexible metadata
    session_duration: 30,
    difficulty_level: 2,
    participant_count: 50,
    notes: "First round of testing"
  }
};

// Experiment response from server (includes nested experiment_type)
const experiment = {
  uuid: "550e8400-e29b-41d4-a716-446655440000",  // string, UUID
  experiment_type_id: 1,                         // number
  description: "Visual stimuli test",            // string
  tags: ["cognitive", "visual"],                 // array of strings
  additional_data: {                             // object
    session_duration: 30,
    difficulty_level: 2,
    participant_count: 50,
    notes: "First round of testing"
  },
  created_at: "2024-01-15T10:30:00Z",            // ISO date string
  updated_at: "2024-01-15T10:30:00Z",            // ISO date string
  experiment_type: {                             // nested experiment type object
    id: 1,
    name: "cognitive_assessment",
    description: "Cognitive evaluation",
    table_name: "cognitive_test_data",
    schema_definition: { /* ... */ },
    created_at: "2024-01-15T10:30:00Z",
    updated_at: "2024-01-15T10:30:00Z"
  }
};
```

### Experiment Data
```javascript
// Experiment data creation (primary JavaScript client use case)
const experimentDataCreate = {
  participant_id: "SUBJ-2024-001",     // string, required, max 100 chars
  data: {                              // object, must match experiment type schema
    reaction_time: 1.23,               // matches schema: FLOAT
    accuracy: 0.85,                    // matches schema: FLOAT
    difficulty_level: 2,               // matches schema: INTEGER
    stimulus_type: "visual"            // matches schema: STRING
  }
};

// Experiment data row response (dynamic schema based on experiment type)
const experimentDataRow = {
  id: 1,                                          // number, auto-generated row ID
  experiment_uuid: "550e8400-e29b-41d4-a716-446655440000",  // string, links to experiment
  participant_id: "SUBJ-2024-001",               // string
  created_at: "2024-01-15T10:30:00Z",           // ISO date string
  updated_at: "2024-01-15T10:30:00Z",           // ISO date string
  // Custom fields based on experiment type schema
  reaction_time: 1.23,                           // FLOAT column
  accuracy: 0.85,                                // FLOAT column
  difficulty_level: 2,                           // INTEGER column
  stimulus_type: "visual"                        // STRING column
};
```

## Python Data Types (Pydantic Models)

The Python client uses Pydantic models for automatic validation, serialization, and type coercion.

### Tag Models
```python
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

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
```

### Experiment Type Models
```python
from typing import Dict, Any, Union, List
from pydantic import field_validator

# Column definition can be simple string or complex object
ColumnDefinition = Union[str, Dict[str, Any]]

class ExperimentTypeCreate(BaseModel):
    """Data for creating a new experiment type."""
    name: str = Field(..., max_length=100, description="Experiment type name")
    table_name: str = Field(..., max_length=100, description="Database table name")
    schema_definition: Dict[str, ColumnDefinition] = Field(
        default_factory=dict, 
        description="Column definitions for experiment data"
    )
    description: Optional[str] = Field(None, description="Experiment type description")
    
    @field_validator('schema_definition')
    def validate_schema_definition(cls, v):
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
                if 'type' not in column_def:
                    raise ValueError(f"Column definition for '{column_name}' must include 'type'")
                if column_def['type'].upper() not in supported_types:
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
```

### Experiment Models
```python
from uuid import UUID
from pydantic import field_validator

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
```

### Experiment Data Models
```python
class ExperimentDataCreate(BaseModel):
    """Data for creating an experiment data row."""
    participant_id: str = Field(..., max_length=100, description="Participant identifier")
    data: Dict[str, Any] = Field(..., description="Experiment data matching type schema")

class ExperimentDataUpdate(BaseModel):
    """Data for updating an experiment data row."""
    participant_id: Optional[str] = Field(None, max_length=100, description="Participant identifier")
    data: Optional[Dict[str, Any]] = Field(None, description="Experiment data updates")

class ExperimentDataRow(BaseModel):
    """Experiment data row response with dynamic schema."""
    model_config = ConfigDict(
        from_attributes=True,
        extra='allow'  # Allow additional fields from dynamic schema
    )
    
    id: int
    experiment_uuid: UUID
    participant_id: str
    created_at: datetime
    updated_at: datetime
    # Additional fields will be added dynamically based on experiment type schema
    
    def get_custom_data(self) -> Dict[str, Any]:
        """Extract custom data fields (excluding standard columns)."""
        standard_fields = {'id', 'experiment_uuid', 'participant_id', 'created_at', 'updated_at'}
        return {k: v for k, v in self.model_dump().items() if k not in standard_fields}

class ExperimentDataQuery(BaseModel):
    """Query parameters for experiment data."""
    participant_id: Optional[str] = Field(None, max_length=100, description="Filter by participant")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Custom field filters")
    created_after: Optional[datetime] = Field(None, description="Filter by creation date (after)")
    created_before: Optional[datetime] = Field(None, description="Filter by creation date (before)")
    limit: int = Field(100, ge=1, le=1000, description="Maximum rows to return")
    offset: int = Field(0, ge=0, description="Number of rows to skip")
```

### Column Information Models
```python
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
```

### Search Models
```python
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
```

### Response Wrapper Models
```python
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
        default_factory=dict,
        description="Metadata per experiment UUID"
    )
    pagination: PaginationInfo
```

### Count and Delete Response Models
```python
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
```

### Version Information Model
```python
class VersionResponse(BaseModel):
    """API version and compatibility information."""
    api_version: str
    client_version: Optional[str] = None
    compatible: Optional[bool] = None
    compatibility_rule: str
    warning: Optional[str] = None
```

## Pydantic Benefits for Python Client

### Automatic Validation
```python
# Automatic validation on creation
try:
    experiment = ExperimentCreate(
        experiment_type_id=1,
        description="Test experiment",
        tags=["cognitive"] * 15  # Too many tags!
    )
except ValidationError as e:
    print(e.errors())  # Clear validation error messages

# Type coercion
experiment = ExperimentCreate(
    experiment_type_id="1",  # String gets converted to int
    description="Test experiment"
)
print(experiment.experiment_type_id)  # 1 (int)
```

### JSON Serialization
```python
# Easy JSON serialization for API requests
experiment_data = ExperimentCreate(
    experiment_type_id=1,
    description="Test experiment",
    tags=["cognitive", "visual"]
)

# Convert to dict for API request
request_body = experiment_data.model_dump()
# {'experiment_type_id': 1, 'description': 'Test experiment', 'tags': ['cognitive', 'visual'], 'additional_data': {}}

# Convert to JSON string
json_body = experiment_data.model_dump_json()
```

### Response Parsing
```python
# Parse API responses into typed objects
api_response = {
    "id": 1,
    "name": "cognitive_test",
    "table_name": "cognitive_data",
    "schema_definition": {"reaction_time": "FLOAT"},
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
}

experiment_type = ExperimentType.model_validate(api_response)
print(experiment_type.created_at)  # datetime object, not string
```

### Configuration and Aliases
```python
# Models can be configured for backend compatibility
class ExperimentResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,    # Allow creation from SQLAlchemy models
        populate_by_name=True,   # Allow both field names and aliases
        extra='forbid'           # Reject unknown fields
    )
    
    uuid: UUID = Field(alias='experiment_uuid')  # Handle field name differences
    type_id: int = Field(alias='experiment_type_id')
```

This Pydantic-based approach provides excellent developer experience with automatic validation, type safety, and seamless JSON handling while maintaining compatibility with the backend API.