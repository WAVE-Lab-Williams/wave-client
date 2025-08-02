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
- **Authentication**: Environment variable-based API keys for both clients (role automatically verified)

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
├── README.md
├── pyproject.toml            # Python config
├── package.json              # JavaScript config
├── Makefile                  # Development commands
├── .github/workflows/        # CI/CD
├── docs/                     # Documentation
├── javascript/               # JS client & tests
├── python/                   # Python client & tests
├── tests/                    # Shared utilities
└── tools/                    # Development tools
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
- [ ] Implement base async HTTP client with httpx (following backend async patterns)
- [ ] Create resource classes for each API endpoint group
- [ ] Implement error handling and retry logic (Unkey rate limiting awareness)
- [ ] Add pagination helpers
- [ ] Implement pandas DataFrame conversion utilities
- [ ] Environment variable-based API key authentication


### 3.3 Resource Implementation
- [ ] `ExperimentTypesResource`: CRUD operations + pandas conversion
- [ ] `ExperimentsResource`: CRUD + filtering + relationship management + pandas conversion
- [ ] `ExperimentDataResource`: Data operations + batch upload + querying + pandas conversion
- [ ] `TagsResource`: CRUD + search functionality
- [ ] `SearchResource`: Advanced search across all resources + pandas conversion

### 3.4 Authentication & Configuration
- [ ] Environment variable-based API key authentication (`WAVE_API_KEY` - role automatically determined)
- [ ] Base URL configuration via environment variables
- [ ] Request timeout and retry configuration (Unkey rate limiting compatible)
- [ ] Environment variable support following backend patterns
- [ ] Version compatibility headers (`X-WAVE-Client-Version` send, `X-WAVE-API-Version` receive)
- [ ] **Server-side compatibility checking**: Backend logs warnings for incompatible versions (semantic versioning rules)
- [ ] **No client-side compatibility matrix needed**: Uses semantic versioning (same major = compatible)

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
│   └── wave-client.test.js    # Comprehensive unit tests
├── examples/
│   └── example.html           # jsPsych integration example
├── test-config.js             # Test configuration and mocking
├── rollup.config.js           # Build configuration
└── package.json               # Dependencies and scripts
```

**Tasks:**
- [x] Create base HTTP client using Fetch API with environment variable API key authentication
- [x] Implement single primary method: `logExperimentData(experimentId, participantId, data)`
- [x] Add generous retry logic with timeout (prevent experimental data loss)
- [x] Add JSDoc documentation for public methods
- [x] Create error handling that works in browser environments
- [x] Support direct jsPsych JSON data logging
- [x] Version compatibility headers (`X-WAVE-Client-Version` send, `X-WAVE-API-Version` receive)
- [x] **Server-side compatibility checking**: Backend handles version validation and logging
- [x] **No client-side compatibility logic needed**: Simple header sending only

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
- **Complete WaveClient class** with authentication, retry logic, and error handling
- **Comprehensive test suite** with 28 passing unit tests including retry, error, and jsPsych integration tests
- **Build system** producing ES6, UMD, and minified distributions
- **Working example** demonstrating jsPsych integration
- **Production ready** with proper error handling and data loss prevention

---

## Phase 5: Testing & Quality Assurance

### 5.1 Unit Testing
- [ ] **Python**: pytest with coverage reporting, following backend patterns
- [ ] **JavaScript**: Jest for unit tests
- [ ] **Shared**: Create test fixtures and mock API responses

### 5.2 Integration Testing
- [ ] Test against live WAVE Backend API (using development instance). Unit tests must SKIP if the localhost url is unavailable.
- [ ] Validate all CRUD operations work correctly
- [ ] Test error handling and edge cases
- [ ] Verify authentication flows

### 5.3 Example Applications
**Tasks:**
- [ ] Create standalone HTML example with jsPsych integration
- [ ] Build Python data analysis example notebook
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

### 6.3 Maintenance & Support
- [ ] Create issue templates for bug reports and feature requests
- [ ] Set up automated dependency updates
- [ ] Plan backward compatibility strategy
- [ ] Design upgrade migration guides

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
