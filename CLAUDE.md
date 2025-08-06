# WAVE Client Library Development Instructions

## Project Overview

Create a dual-language client library (JavaScript + Python) for the WAVE Backend API, designed for psychology and behavioral experiment data logging. The JavaScript client will be used in vanilla HTML frontends with jsPsych integration, while the Python client will support research data analysis workflows.

## Key Requirements

### Technology Stack
- **JavaScript**: Pure ES6 (no TypeScript), ES6 modules + UMD builds for browser compatibility, **experiment data logging only**
- **Python**: Python 3.12 with UV package manager, type hints with runtime validation, pandas integration
- **Distribution**: GitHub Releases with built assets (JavaScript files + Python wheels), jsDelivr CDN integration
- **Installation**: Release-based distribution (internal tool, no npm/PyPI publishing)
- **Frontend Integration**: Direct browser usage via CDN, jsPsych compatibility
- **Authentication**: URL parameter-based API keys for JavaScript client, environment variables for Python client (roles automatically verified)

### Reference Materials
- **API Documentation**: `local/docs/api-usage.md` and `local/docs/database-schema.md` in wave-backend repo
- **Backend Implementation**: `local/wave_backend/` folder for API patterns and data models
- **Development Patterns**: `Makefile` in wave-backend repo for UV usage patterns

### Server-Side Versioning (✅ COMPLETED)
The backend already implements lightweight version compatibility checking:
- **HTTP Headers**: `X-WAVE-Client-Version` (request) and `X-WAVE-API-Version` (response)
- **Semantic Versioning**: Same major version = compatible (1.x.x ↔ 1.y.z), different major = incompatible
- **Non-blocking**: Server logs warnings for incompatible versions but allows requests
- **Endpoint**: `/version` provides compatibility information
- **Middleware**: Automatic header processing and logging for all requests

## Distribution Strategy

### GitHub Releases Approach
For this internal research tool, we use **GitHub Releases** instead of public package repositories:

**JavaScript Distribution:**
- Built files (ESM, UMD, minified) attached to GitHub releases
- Served via jsDelivr CDN: `https://cdn.jsdelivr.net/gh/WAVE-Lab-Williams/wave-client@v1.0.0/wave-client.esm.js`
- No npm publishing required - keeps tool internal to lab

**Python Distribution:**
- Python wheels (.whl) attached to GitHub releases
- Direct installation: `pip install https://github.com/WAVE-Lab-Williams/wave-client/releases/download/v1.0.0/wave_client-1.0.0-py3-none-any.whl`
- No PyPI publishing required - maintains internal access control

**Release Workflow:**
1. Developer runs: `make release VERSION=v1.0.0`
2. GitHub Actions builds and attaches assets automatically
3. Users reference specific versions in their code
4. jsDelivr serves JavaScript files directly from GitHub releases

---

## Phase 1: Repository Setup & Structure

### 1.1 Initial Repository Structure
Create the following directory structure in this mostly empty repository:

```
wave-client/
├── README.md                 # User-facing documentation
├── CLAUDE.md                # Development instructions (this file)
├── LICENSE.txt              # MIT license
├── .env.example             # Environment variable template
├── .gitignore               # Git ignore patterns
├── .python-version          # Python 3.12
├── package.json             # JavaScript project config & dependencies
├── pyproject.toml           # Python project config & dependencies  
├── uv.lock                  # Python dependency lock file
├── rollup.config.js         # JavaScript build configuration
├── Makefile                 # Development commands
├── .github/
│   └── workflows/           # CI/CD workflows
├── docs/                    # Documentation
│   ├── api-endpoints.md     # Complete API reference
│   ├── api-reference.md     # Auto-generated docs
│   ├── client-schemas.md    # Request/response schemas
│   ├── data-types.md        # Pydantic models & JS schemas
│   ├── error-handling.md    # Error classes & retry logic
│   ├── examples.md          # Usage examples
│   ├── installation.md     # Setup instructions
│   ├── method-naming.md     # API surface conventions
│   └── pandas-integration.md # DataFrame conversion guide
├── javascript/              # JavaScript client & build system
│   ├── dist/                # Built files (ESM, UMD, minified)
│   ├── examples/
│   │   └── example.html     # jsPsych integration demo
│   ├── src/
│   │   ├── wave-client.js   # Main client (experiment data logging)
│   │   └── core/
│   │       └── errors.js    # Error classes
│   ├── tests/               # Jest test suites
│   │   ├── test-config.js   # Test configuration & mocking
│   │   ├── test-utils.js    # Shared test utilities
│   │   ├── small/           # Unit tests (fast, mocked)
│   │   │   ├── constructor.test.js
│   │   │   ├── error-handling.test.js
│   │   │   ├── experiment-data.test.js
│   │   │   ├── jspsych-data.test.js
│   │   │   ├── url-authentication.test.js
│   │   │   └── utility-methods.test.js
│   │   └── medium/          # Integration tests (real API calls)
│   │       └── integration.test.js
│   └── rollup.config.js     # Build configuration
├── python/                  # Python client & testing
│   ├── tests/
│   │   ├── conftest.py      # Pytest configuration
│   │   ├── small/           # Unit tests
│   │   │   ├── conftest.py
│   │   │   ├── test_client.py
│   │   │   └── test_pandas_utils.py
│   │   └── medium/          # Integration tests
│   │       ├── conftest.py
│   │       └── test_integration.py
│   ├── wave_client/         # Main package
│   │   ├── __init__.py      # Package exports
│   │   ├── client.py        # Main async client class
│   │   ├── exceptions.py    # Error classes
│   │   ├── models/          # Pydantic data models
│   │   │   ├── __init__.py
│   │   │   ├── base.py      # Base model classes
│   │   │   ├── responses.py # API response models
│   │   │   └── search.py    # Search-specific models
│   │   ├── resources/       # API resource classes
│   │   │   ├── __init__.py
│   │   │   ├── base.py      # Base resource class
│   │   │   ├── experiment_data.py # Data operations + pandas
│   │   │   ├── experiment_types.py # CRUD + pandas
│   │   │   ├── experiments.py # CRUD + filtering + pandas
│   │   │   ├── search.py    # Advanced search + pandas
│   │   │   └── tags.py      # CRUD + search
│   │   └── utils/           # Utilities
│   │       ├── __init__.py
│   │       ├── http_client.py # Async HTTP with retry logic
│   │       ├── pandas_utils.py # DataFrame conversion
│   │       └── versioning.py # Version compatibility
│   └── wave_client.egg-info/ # Package metadata
├── tools/                   # Development tools
└── local/                   # Backend reference (ignored by git)
    ├── docs/
    │   ├── api-usage.md     # Backend API documentation
    │   └── database-schema.md # Database schema reference  
    └── wave_backend/        # Backend codebase reference
        ├── api/
        ├── auth/
        ├── models/
        ├── schemas/
        ├── services/
        └── utils/
```

### 1.2 Core Configuration Files

**Tasks:**
- [x] Create `README.md` with installation instructions for both languages
- [x] Set up `pyproject.toml` with UV configuration and Python 3.12 requirement
- [x] Create `.python-version` file with Python 3.12
- [x] Create `.gitignore` for Python, JavaScript, editor files, and local folder
- [x] Set up GitHub Actions workflows for testing both languages (basic testing only)
- [x] Create `.env.example` with environment variables (WAVE_API_KEY, WAVE_API_URL)
- [x] Create directory structure (docs/, javascript/, python/, tests/, tools/)
- [x] Create documentation stubs (installation.md, examples.md, api-reference.md)

---

## Phase 2: API Analysis & Type Definitions ✅ COMPLETED

### 2.1 API Endpoint Mapping ✅ COMPLETED
Based on `local/docs/api-usage.md`, mapped all endpoints to client methods:

**Core Resources:**
- **JavaScript Client**: Experiment data logging only (role determined by API key)
- **Python Client**: Full API access (role determined by API key)
  - **Experiment Types**: Create, read, update, delete, get schema info
  - **Experiments**: Create, read, update, delete, get by filters
  - **Experiment Data**: Add data rows, query data, update rows, batch operations, pandas conversion
  - **Tags**: Create, read, update, delete, search
  - **Search**: Advanced search across experiments, types, data, and tags

**Tasks:**
- [x] Document all API endpoints from the backend routes (23 endpoints across 5 resource groups)
- [x] Define request/response schemas for each endpoint
- [x] Create method naming conventions that work for both JS and Python
- [x] Map error codes to client-specific error classes
- [x] Design retry logic with timeout and retry limits (generous defaults for JavaScript to prevent data loss)

### 2.2 Data Models ✅ COMPLETED
Created consistent data models based on `local/wave_backend/schemas/` and `local/wave_backend/models/`:

**Tasks:**
- [x] Define core data types (ExperimentType, Experiment, ExperimentData, Tag) using Pydantic models
- [x] Create response wrappers for pagination and metadata
- [x] Plan error handling strategies with intelligent retry logic
- [x] Design pandas DataFrame conversion utilities for Python client (functional .pipe() approach)
- [x] **Note**: No client-side validation needed (server-side validation only)

**Documentation Created:**
- `docs/api-endpoints.md` - Complete API reference (23 endpoints)
- `docs/client-schemas.md` - Request/response schemas for both languages
- `docs/method-naming.md` - Method naming conventions and API surface
- `docs/error-handling.md` - Error classes, retry logic, and recovery strategies
- `docs/data-types.md` - Pydantic models and JavaScript object schemas
- `docs/pandas-integration.md` - Simple API-to-DataFrame conversion for functional pipelines

---

## Phase 3: Python Client Development

### 3.1 Project Setup
Following the UV patterns from the backend Makefile:

**Tasks:**
- [x] Set up `python/pyproject.toml` with UV configuration and Python 3.12 requirement
- [x] Create virtual environment management scripts
- [x] Set up testing framework (pytest) with proper coverage
- [x] Configure linting (black, isort, flake8, pylint) matching backend patterns
- [ ] Add pandas and httpx as dependencies (async HTTP client + DataFrame conversion)

### 3.2 Core Architecture

**Directory Structure:**
```
python/
├── wave_client/
│   ├── __init__.py
│   ├── client.py              # Main client class
│   ├── auth/
│   ├── resources/
│   ├── utils/
├── tests/
└── examples/
```

**Tasks:**
- [x] Implement base async HTTP client with httpx (following backend async patterns)
- [x] Create resource classes for each API endpoint group
- [x] Implement error handling and retry logic (Unkey rate limiting awareness)
- [x] Add pagination helpers
- [x] Implement pandas DataFrame conversion utilities
- [x] Environment variable-based API key authentication


### 3.3 Resource Implementation ✅ COMPLETED
- [x] `ExperimentTypesResource`: CRUD operations + pandas conversion
- [x] `ExperimentsResource`: CRUD + filtering + relationship management + pandas conversion
- [x] `ExperimentDataResource`: Data operations + batch upload + querying + pandas conversion
- [x] `TagsResource`: CRUD + search functionality
- [x] `SearchResource`: Advanced search across all resources + pandas conversion

### 3.4 Authentication & Configuration ✅ COMPLETED
- [x] Environment variable-based API key authentication (`WAVE_API_KEY` - role automatically determined)
- [x] Base URL configuration via environment variables
- [x] Request timeout and retry configuration (Unkey rate limiting compatible)
- [x] Environment variable support following backend patterns
- [x] Version compatibility headers (`X-WAVE-Client-Version` send, `X-WAVE-API-Version` receive)
- [x] **Server-side compatibility checking**: Backend logs warnings for incompatible versions (semantic versioning rules)
- [x] **No client-side compatibility matrix needed**: Uses semantic versioning (same major = compatible)

**Implementation Summary:**
- **Complete async HTTP client** with httpx, authentication, and comprehensive retry logic
- **Resource-based architecture** with 5 resource classes covering all 23 API endpoints
- **Pandas-first approach** - all data methods return DataFrames by default for immediate analysis
- **Comprehensive error handling** with specific exception classes and retry strategies
- **Version compatibility system** integrated with server-side semantic versioning
- **Extensive documentation** targeted at inexperienced researchers with clear examples
- **Production ready** with proper context manager support and resource cleanup
- **Complete test coverage** with 62 unit tests and 3 integration tests

---

## Phase 4: JavaScript Client Development ✅ COMPLETED

### 4.1 Build System Setup ✅ COMPLETED
Created a simple build system without TypeScript:

**Tasks:**
- [x] Set up Rollup configuration for ES6 modules and UMD builds
- [x] Configure minification and source maps
- [x] Create development and production build scripts
- [x] Set up browser testing with Jest (not Playwright - using Jest for unit tests)

### 4.2 Core Architecture - **Simplified for Experiment Data Only** ✅ COMPLETED

**Directory Structure:**
```
javascript/
├── src/
│   ├── wave-client.js         # Main entry point - experiment data logging only
│   ├── core/
│   │   └── errors.js          # Error classes
├── dist/                      # Built files (ESM, UMD, minified)
├── tests/
│   ├── test-config.js         # Test configuration and mocking
│   └── wave-client.test.js    # Comprehensive unit tests
├── examples/
│   └── example.html           # jsPsych integration example
├── rollup.config.js           # Build configuration
└── package.json               # Dependencies and scripts
```

**Tasks:**
- [x] Create base HTTP client using Fetch API with **URL parameter-based API key authentication**
- [x] Implement single primary method: `logExperimentData(experimentId, participantId, data)`
- [x] Add generous retry logic with timeout (prevent experimental data loss)
- [x] Add JSDoc documentation for public methods
- [x] Create error handling that works in browser environments
- [x] Support direct jsPsych JSON data logging
- [x] Version compatibility headers (`X-WAVE-Client-Version` send, `X-WAVE-API-Version` receive)
- [x] **Server-side compatibility checking**: Backend handles version validation and logging
- [x] **No client-side compatibility logic needed**: Simple header sending only

**Security Enhancement:**
- **URL-based API Key Extraction**: Client extracts experimentee API key from URL parameters (`?key=exp_abc123`)
- **Browser Security**: Avoids exposing API keys in JavaScript bundles or environment variables
- **Session-specific Keys**: Each experiment session gets a unique temporary key via URL
- **Backward Compatibility**: Maintains support for explicit `apiKey` option parameter

### 4.3 Browser Compatibility ✅ COMPLETED
- [x] Ensure ES6 module support
- [x] Create UMD build for `<script>` tag usage
- [x] Test cross-browser compatibility (AbortSignal fallback for older environments)
- [x] Validate bundle size and performance (under 25KB minified)

### 4.4 jsPsych Integration ✅ COMPLETED
**Tasks:**
- [x] Create simple helper to convert jsPsych trial JSON data to API format (`fromJsPsychData`)
- [x] Design workflow: `jsPsychData → logExperimentData(experimentId, participantId, jsPsychData)`
- [x] Implement batch data upload capability (single data object per call)
- [x] Create example jsPsych experiments using the client (`examples/example.html`)
- [x] Ensure robust error handling to prevent data loss during experiments
- [x] **No dedicated jsPsych plugin needed** - just direct JSON data logging

**Implementation Summary:**
- **Complete WaveClient class** with URL-based authentication, retry logic, and error handling
- **Comprehensive test suite** with 62 unit tests and 3 integration tests (separated into small/medium)
- **Build system** producing ES6, UMD, and minified distributions
- **Working example** demonstrating jsPsych integration with URL parameter authentication
- **Production ready** with proper error handling and data loss prevention
- **Enhanced Security Model**: URL parameter-based API key extraction for browser experiments
- **Test separation**: Unit tests in `javascript/tests/small/`, integration tests in `javascript/tests/medium/`

---

## Phase 5: Testing & Quality Assurance ✅ COMPLETED

### 5.1 Unit Testing ✅ COMPLETED
- [x] **Python**: pytest with coverage reporting, following backend patterns
- [x] **JavaScript**: Jest with small/medium test separation for unit tests
- [x] **Shared**: Create test fixtures and mock API responses

### 5.2 Integration Testing ✅ COMPLETED
- [x] Test against live WAVE Backend API (using development instance). Unit tests must SKIP if the localhost url is unavailable.
- [x] Graceful skipping when localhost backend is unavailable
- [x] Validate all CRUD operations work correctly
- [x] Test error handling and edge cases
- [x] Verify authentication flows

### 5.3 Example Applications ✅ COMPLETED
**Tasks:**
- [x] Create standalone HTML example with jsPsych integration
- [x] Build Python data analysis example notebook
- [ ] Create end-to-end workflow examples
- [ ] Document common usage patterns

---

## Phase 6: Documentation & Distribution

### 6.1 Documentation
- [ ] **Documentation System Setup**: Unified auto-documentation approach
  - [ ] Configure Sphinx + autodoc for Python client (add to dev dependencies)
  - [ ] Set up JSDoc for JavaScript client (add to package.json devDependencies)
  - [ ] Configure docsify for unified documentation site
  - [ ] Create `docs/conf.py` for Sphinx configuration
  - [ ] Add Makefile targets for generating docs from both clients
  - [ ] Structure: `docs/python/` (Sphinx), `docs/javascript/` (JSDoc), main `api-reference.md` links both
- [ ] **Installation Guide**: GitHub-based installation for both languages
- [ ] **API Reference**: Auto-generated from code documentation (Sphinx + JSDoc)
- [ ] **Examples Library**: Real-world usage examples
- [ ] **jsPsych Integration Guide**: Specific integration patterns

### 6.2 GitHub Release Distribution Setup
**Tasks:**
- [ ] Create GitHub Actions workflow for automated releases (`.github/workflows/release.yml`)
  - [ ] Build JavaScript files (ESM, UMD, minified) on tag push
  - [ ] Build Python wheel (.whl) files
  - [ ] Attach built assets to GitHub releases
  - [ ] Support semantic versioning (v1.0.0 format)
- [ ] Configure jsDelivr CDN access via GitHub releases
  - [ ] JavaScript: `https://cdn.jsdelivr.net/gh/WAVE-Lab-Williams/wave-client@v1.0.0/wave-client.esm.js`
  - [ ] Python: `https://github.com/WAVE-Lab-Williams/wave-client/releases/download/v1.0.0/wave_client-1.0.0-py3-none-any.whl`
- [ ] Test the complete release workflow:
- [ ] 
---

## Development Guidelines

### Code Quality Standards
- **Python**: Follow backend patterns (black, isort, flake8, pylint)
- **JavaScript**: ESLint configuration, JSDoc for documentation
- **Testing**: Minimum 80% code coverage for both languages
- **Documentation**: All public methods must have examples

### Version Management
- **Semantic Versioning**: Use MAJOR.MINOR.PATCH format for both clients
- **Compatibility Rules**: Same major version = compatible, different major = breaking changes
- **Server-Side Validation**: Backend automatically checks and logs compatibility warnings
- **Client Implementation**: Simply send `X-WAVE-Client-Version` header, no client-side logic needed
- **Coordinated Releases**: Align JavaScript and Python client version numbers where possible

### Performance Requirements
- **JavaScript**: Bundle size under 25KB minified (simplified client), generous retry timeouts to prevent data loss
- **Python**: Response times under 100ms for simple operations, efficient pandas DataFrame conversion
- **Both**: Support batch operations for large datasets, Unkey rate limiting awareness

## Claude Memories

### Development Insights
- Memorized the intricate design considerations for creating a dual-language client library for a research data logging backend
- Recognized the unique requirements of supporting both JavaScript (for frontend experiments) and Python (for data analysis) clients
