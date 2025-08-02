# WAVE Backend API Endpoints Reference

This document provides a comprehensive reference for all WAVE Backend API endpoints, organized by resource type. This serves as the basis for implementing both JavaScript and Python client libraries.

## Base Configuration

- **Base URL**: `http://localhost:8000` (development) or configured via `WAVE_API_URL`
- **Authentication**: 
  - **JavaScript Client**: Bearer token via `Authorization: Bearer {API_KEY}` extracted from URL parameter (`?key=exp_abc123`)
  - **Python Client**: Bearer token via `Authorization: Bearer {API_KEY}` from `WAVE_API_KEY` environment variable
  - **Role Verification**: API key role is automatically verified by the backend
- **Versioning**: Send `X-WAVE-Client-Version` header, receive `X-WAVE-API-Version` response header
- **Content-Type**: `application/json` for all requests/responses

## Authentication Security Model

### JavaScript Client (Browser-based)
- **URL Parameter Extraction**: API key extracted from `?key=` or `#key=` URL parameter
- **Security Benefits**: 
  - No API keys exposed in JavaScript source code or bundles
  - Each experiment session gets unique temporary key
  - Prevents accidental exposure in version control
- **Example Usage**: `https://experiment-site.com/task.html?key=exp_abc123&participant=P001`

### Python Client (Server-side)
- **Environment Variable**: Uses `WAVE_API_KEY` environment variable
- **Suitable for**: Data analysis, batch processing, server-side operations
- **Full API Access**: Can access all endpoints based on API key role

## System Endpoints

### GET `/`
- **Purpose**: API root welcome message
- **Auth**: None required
- **Response**: `{"message": "Welcome to the WAVE Backend API", "version": "1.0.0"}`

### GET `/health`
- **Purpose**: Health check for monitoring
- **Auth**: None required  
- **Response**: `{"status": "healthy", "service": "wave-backend"}`

### GET `/version`
- **Purpose**: Version compatibility checking
- **Auth**: None required
- **Headers**: Optional `X-WAVE-Client-Version`
- **Response**: 
```json
{
  "api_version": "1.0.0",
  "client_version": "1.0.0",
  "compatible": true,
  "compatibility_rule": "Semantic versioning: same major version = compatible"
}
```

## Experiment Types Resource

**Purpose**: Manage experiment type templates that define data schemas

### POST `/api/v1/experiment-types/`
- **Auth**: RESEARCHER+
- **Purpose**: Create new experiment type with schema definition
- **Request Body**:
```json
{
  "name": "cognitive_assessment",
  "description": "Cognitive performance evaluation",
  "table_name": "cognitive_test_data",
  "schema_definition": {
    "reaction_time": "FLOAT",
    "accuracy": "FLOAT",
    "difficulty_level": "INTEGER",
    "stimulus_type": "STRING"
  }
}
```
- **Response**: ExperimentTypeResponse with created entity
- **Errors**: 400 (duplicate name/table_name, invalid schema)

### GET `/api/v1/experiment-types/{experiment_type_id}`
- **Auth**: RESEARCHER+
- **Purpose**: Get specific experiment type by ID
- **Response**: ExperimentTypeResponse
- **Errors**: 404 (not found)

### GET `/api/v1/experiment-types/`
- **Auth**: RESEARCHER+
- **Purpose**: List experiment types with pagination
- **Query Params**: `skip` (default: 0), `limit` (default: 100, max: 1000)
- **Response**: List[ExperimentTypeResponse]

### PUT `/api/v1/experiment-types/{experiment_type_id}`
- **Auth**: RESEARCHER+
- **Purpose**: Update experiment type (name, description, schema)
- **Request Body**: ExperimentTypeUpdate (partial)
- **Response**: ExperimentTypeResponse
- **Errors**: 400 (name conflict), 404 (not found)

### DELETE `/api/v1/experiment-types/{experiment_type_id}`
- **Auth**: RESEARCHER+
- **Purpose**: Delete experiment type
- **Response**: `{"message": "Experiment type deleted successfully"}`
- **Errors**: 404 (not found)

### GET `/api/v1/experiment-types/name/{experiment_type_name}/columns`
- **Auth**: RESEARCHER+
- **Purpose**: Get schema info for experiment type by name
- **Response**: ExperimentColumnsResponse
- **Errors**: 404 (not found)

## Tags Resource

**Purpose**: Manage categorization tags for experiments

### POST `/api/v1/tags/`
- **Auth**: RESEARCHER+
- **Purpose**: Create new categorization tag
- **Request Body**:
```json
{
  "name": "cognitive",
  "description": "Cognitive performance experiments"
}
```
- **Response**: TagResponse
- **Errors**: 400 (duplicate name)

### GET `/api/v1/tags/{tag_id}`
- **Auth**: RESEARCHER+
- **Purpose**: Get specific tag by ID
- **Response**: TagResponse
- **Errors**: 404 (not found)

### GET `/api/v1/tags/`
- **Auth**: RESEARCHER+
- **Purpose**: List tags with pagination
- **Query Params**: `skip` (default: 0), `limit` (default: 100, max: 1000)
- **Response**: List[TagResponse]

### PUT `/api/v1/tags/{tag_id}`
- **Auth**: RESEARCHER+
- **Purpose**: Update tag name/description
- **Request Body**: TagUpdate (partial)
- **Response**: TagResponse
- **Errors**: 400 (name conflict), 404 (not found)

### DELETE `/api/v1/tags/{tag_id}`
- **Auth**: RESEARCHER+
- **Purpose**: Delete tag
- **Response**: `{"message": "Tag deleted successfully"}`
- **Errors**: 404 (not found)

## Experiments Resource

**Purpose**: Manage individual experiment instances

### POST `/api/v1/experiments/`
- **Auth**: RESEARCHER+
- **Purpose**: Create new experiment instance
- **Request Body**:
```json
{
  "experiment_type_id": 1,
  "description": "Cognitive assessment with visual stimuli",
  "tags": ["cognitive", "visual"],
  "additional_data": {
    "session_duration": 30,
    "difficulty_level": 2
  }
}
```
- **Response**: ExperimentResponse
- **Errors**: 400 (invalid experiment_type_id)

### GET `/api/v1/experiments/{experiment_uuid}`
- **Auth**: RESEARCHER+
- **Purpose**: Get specific experiment by UUID
- **Response**: ExperimentResponse
- **Errors**: 404 (not found)

### GET `/api/v1/experiments/`
- **Auth**: RESEARCHER+
- **Purpose**: List experiments with filtering
- **Query Params**: 
  - `skip` (default: 0), `limit` (default: 100, max: 1000)
  - `experiment_type_id` (optional filter)
  - `tags` (optional filter, multiple values)
- **Response**: List[ExperimentResponse]

### PUT `/api/v1/experiments/{experiment_uuid}`
- **Auth**: RESEARCHER+
- **Purpose**: Update experiment description/tags/additional_data
- **Request Body**: ExperimentUpdate (partial)
- **Response**: ExperimentResponse
- **Errors**: 404 (not found)

### DELETE `/api/v1/experiments/{experiment_uuid}`
- **Auth**: ADMIN+
- **Purpose**: Delete experiment (high privilege required)
- **Response**: `{"message": "Experiment deleted successfully"}`
- **Errors**: 404 (not found)

### GET `/api/v1/experiments/{experiment_uuid}/columns`
- **Auth**: RESEARCHER+
- **Purpose**: Get data schema info for experiment
- **Response**: ExperimentColumnsResponse
- **Errors**: 404 (not found)

## Experiment Data Resource

**Purpose**: Manage experiment data rows (EXPERIMENTEE role for creation)

### POST `/api/v1/experiment-data/{experiment_id}/data/`
- **Auth**: EXPERIMENTEE+ (⭐ Key endpoint for JavaScript client)
- **Purpose**: Add new data row to experiment
- **Request Body**:
```json
{
  "participant_id": "SUBJ-2024-001",
  "data": {
    "reaction_time": 1.23,
    "accuracy": 0.85,
    "difficulty_level": 2,
    "stimulus_type": "visual"
  }
}
```
- **Response**: Complete data row with all fields (id, timestamps, experiment_uuid, etc.)
- **Errors**: 400 (validation errors), 404 (experiment not found)

### GET `/api/v1/experiment-data/{experiment_id}/data/`
- **Auth**: RESEARCHER+
- **Purpose**: List experiment data with filtering
- **Query Params**:
  - `participant_id` (optional filter)
  - `created_after`, `created_before` (optional date filters)
  - `limit` (default: 100, max: 1000), `offset` (default: 0)
- **Response**: List[Dict[str, Any]] (dynamic schema based on experiment type)

### GET `/api/v1/experiment-data/{experiment_id}/data/count`
- **Auth**: RESEARCHER+
- **Purpose**: Count data rows with filtering
- **Query Params**: `participant_id` (optional filter)
- **Response**: ExperimentDataCountResponse

### GET `/api/v1/experiment-data/{experiment_id}/data/columns`
- **Auth**: RESEARCHER+
- **Purpose**: Get detailed column schema info
- **Response**: List[ColumnTypeInfo]

### GET `/api/v1/experiment-data/{experiment_id}/data/row/{row_id}`
- **Auth**: RESEARCHER+
- **Purpose**: Get specific data row by ID
- **Response**: Dict[str, Any] (complete row data)
- **Errors**: 404 (not found)

### PUT `/api/v1/experiment-data/{experiment_id}/data/row/{row_id}`
- **Auth**: RESEARCHER+
- **Purpose**: Update specific data row
- **Request Body**: ExperimentDataUpdate (partial)
- **Response**: Dict[str, Any] (updated row data)
- **Errors**: 404 (not found)

### DELETE `/api/v1/experiment-data/{experiment_id}/data/row/{row_id}`
- **Auth**: RESEARCHER+
- **Purpose**: Delete specific data row
- **Response**: ExperimentDataDeleteResponse
- **Errors**: 404 (not found)

### POST `/api/v1/experiment-data/{experiment_id}/data/query`
- **Auth**: RESEARCHER+
- **Purpose**: Advanced data querying with custom filters
- **Request Body**:
```json
{
  "participant_id": "SUBJ-2024-001",
  "filters": {
    "difficulty_level": 2,
    "accuracy": 0.85
  },
  "created_after": "2024-01-01T00:00:00",
  "limit": 100,
  "offset": 0
}
```
- **Response**: List[Dict[str, Any]] (matching rows)

## Search Resource

**Purpose**: Advanced search and querying across all resources

### POST `/api/v1/search/experiments/by-tags`
- **Auth**: RESEARCHER+
- **Purpose**: Find experiments by tag criteria
- **Request Body**:
```json
{
  "tags": ["cognitive", "memory"],
  "match_all": true,
  "created_after": "2024-01-01T00:00:00Z",
  "skip": 0,
  "limit": 100
}
```
- **Response**: ExperimentTagSearchResponse

### POST `/api/v1/search/experiment-types/by-description`
- **Auth**: RESEARCHER+
- **Purpose**: Search experiment types by text
- **Request Body**: ExperimentTypeSearchRequest
- **Response**: ExperimentTypeSearchResponse

### POST `/api/v1/search/tags/by-name`
- **Auth**: RESEARCHER+
- **Purpose**: Search tags by name/description
- **Request Body**: TagSearchRequest
- **Response**: TagSearchResponse

### POST `/api/v1/search/experiments/by-description-and-type`
- **Auth**: RESEARCHER+
- **Purpose**: Search experiment descriptions within specific type
- **Request Body**: ExperimentDescriptionSearchRequest
- **Response**: ExperimentTagSearchResponse

### POST `/api/v1/search/experiments/advanced`
- **Auth**: RESEARCHER+
- **Purpose**: Multi-criteria experiment search
- **Request Body**: AdvancedExperimentSearchRequest
- **Response**: ExperimentTagSearchResponse

### POST `/api/v1/search/experiment-data/by-tags`
- **Auth**: RESEARCHER+
- **Purpose**: Get experiment data for experiments matching tags
- **Request Body**: ExperimentDataByTagsRequest
- **Response**: ExperimentDataByTagsResponse (includes data + metadata)

## Client Implementation Notes

### JavaScript Client Focus:
- **Primary Use**: POST `/api/v1/experiment-data/{experiment_id}/data/` (EXPERIMENTEE role)
- **Method**: `logExperimentData(experimentId, participantId, data)`
- **Error Handling**: Generous retry logic to prevent data loss during experiments
- **Authentication**: Environment variable-based API key

### Python Client Coverage:
- **Full API Access**: All endpoints organized into 5 resource classes
- **Pandas Integration**: DataFrame conversion for all data endpoints
- **Async Support**: httpx-based async HTTP client
- **Type Safety**: Complete type hints and runtime validation

### Common Patterns:
- **Pagination**: All list endpoints support skip/limit with reasonable defaults
- **Date Filtering**: created_after/created_before supported where applicable
- **Error Codes**: Consistent 401/403/404/400/500 patterns across all endpoints
- **Version Compatibility**: Semantic versioning with server-side validation