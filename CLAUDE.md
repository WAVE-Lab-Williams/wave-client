# WAVE Client Library Development Instructions

## Project Overview

Create a dual-language client library (JavaScript + Python) for the WAVE Backend API, designed for psychology and behavioral experiment data logging. The JavaScript client will be used in vanilla HTML frontends with jsPsych integration, while the Python client will support research data analysis workflows.

## Key Requirements

### Technology Stack
- **JavaScript**: Pure ES6 (no TypeScript), ES6 modules + UMD builds for browser compatibility, **experiment data logging only**
- **Python**: Python 3.12 with UV package manager, type hints with runtime validation, pandas integration
- **Installation**: GitHub-based installation (internal distribution, no npm/PyPI)
- **Frontend Integration**: Direct browser usage, jsPsych compatibility, Git submodule support
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

## Phase 2: API Analysis & Type Definitions

### 2.1 API Endpoint Mapping
Based on `local/docs/api-usage.md`, map all endpoints to client methods:

**Core Resources:**
- **JavaScript Client**: Experiment data logging only (role determined by API key)
- **Python Client**: Full API access (role determined by API key)
  - **Experiment Types**: Create, read, update, delete, get schema info
  - **Experiments**: Create, read, update, delete, get by filters
  - **Experiment Data**: Add data rows, query data, update rows, batch operations, pandas conversion
  - **Tags**: Create, read, update, delete, search
  - **Search**: Advanced search across experiments, types, data, and tags

**Tasks:**
- [ ] Document all API endpoints from the backend routes
- [ ] Define request/response schemas for each endpoint
- [ ] Create method naming conventions that work for both JS and Python
- [ ] Map error codes to client-specific error classes
- [ ] Design retry logic with timeout and retry limits (generous defaults for JavaScript to prevent data loss)

### 2.2 Data Models
Create consistent data models based on `local/wave_backend/schemas/` and `local/wave_backend/models/`:

**Tasks:**
- [ ] Define core data types (ExperimentType, Experiment, ExperimentData, Tag)
- [ ] Create response wrappers for pagination and metadata
- [ ] Plan error handling strategies
- [ ] Design pandas DataFrame conversion utilities for Python client
- [ ] **Note**: No client-side validation needed (server-side validation only)

---

## Phase 3: Python Client Development

### 3.1 Project Setup
Following the UV patterns from the backend Makefile:

**Tasks:**
- [ ] Set up `python/pyproject.toml` with UV configuration and Python 3.12 requirement
- [ ] Create virtual environment management scripts
- [ ] Set up testing framework (pytest) with proper coverage
- [ ] Configure linting (black, isort, flake8, pylint) matching backend patterns
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

## Phase 4: JavaScript Client Development

### 4.1 Build System Setup
Create a simple build system without TypeScript:

**Tasks:**
- [ ] Set up Rollup configuration for ES6 modules and UMD builds
- [ ] Configure minification and source maps
- [ ] Create development and production build scripts
- [ ] Set up browser testing with Playwright

### 4.2 Core Architecture - **Simplified for Experiment Data Only**

**Directory Structure:**
```
javascript/
├── src/
│   ├── wave-client.js         # Main entry point - experiment data logging only
│   ├── core/
│   │   ├── client.js          # Base HTTP client
│   │   ├── auth.js            # Role.EXPERIMENTEE authentication
│   │   └── errors.js          # Error classes
│   └── utils/
│       ├── retry.js           # Generous retry logic for data preservation
│       └── validation.js      # Basic input validation
├── dist/                      # Built files
├── tests/
└── examples/
```

**Tasks:**
- [ ] Create base HTTP client using Fetch API with environment variable API key authentication
- [ ] Implement single primary method: `logExperimentData(experimentId, participantId, data)`
- [ ] Add generous retry logic with timeout (prevent experimental data loss)
- [ ] Add JSDoc documentation for public methods
- [ ] Create error handling that works in browser environments
- [ ] Support direct jsPsych JSON data logging
- [ ] Version compatibility headers (`X-WAVE-Client-Version` send, `X-WAVE-API-Version` receive)
- [ ] **Server-side compatibility checking**: Backend handles version validation and logging
- [ ] **No client-side compatibility logic needed**: Simple header sending only

### 4.3 Browser Compatibility
- [ ] Ensure ES6 module support
- [ ] Create UMD build for `<script>` tag usage
- [ ] Test cross-browser compatibility (Chrome, Firefox, Safari, Edge)
- [ ] Validate bundle size and performance

### 4.4 jsPsych Integration
**Tasks:**
- [ ] Create simple helper to convert jsPsych trial JSON data to API format
- [ ] Design workflow: `jsPsychData → logExperimentData(experimentId, participantId, jsPsychData)`
- [ ] Implement batch data upload for performance (multiple trials at once)
- [ ] Create example jsPsych experiments using the client
- [ ] Ensure robust error handling to prevent data loss during experiments
- [ ] **No dedicated jsPsych plugin needed** - just direct JSON data logging

---

## Phase 5: Testing & Quality Assurance

### 5.1 Unit Testing
- [ ] **Python**: pytest with coverage reporting, following backend patterns
- [ ] **JavaScript**: Jest for unit tests, Playwright for browser tests
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
- [ ] **Installation Guide**: GitHub-based installation for both languages
- [ ] **API Reference**: Auto-generated from code documentation
- [ ] **Examples Library**: Real-world usage examples
- [ ] **jsPsych Integration Guide**: Specific integration patterns

### 6.2 GitHub Distribution Setup
**Tasks:**
- [ ] Set up GitHub releases with semantic versioning
- [ ] Configure jsDelivr CDN access for JavaScript files
- [ ] Create installation documentation for Git submodule usage
- [ ] Set up automated release processes

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
