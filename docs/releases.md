# WAVE Client Release Process

## Overview

The WAVE Client uses a fully automated release system that builds and distributes both JavaScript and Python clients whenever a new v3. **Tag Content**: Verify built files are present in the release branch at the tagged commitrsion is detected on the main branch. The system creates CDN-ready JavaScript builds and Python wheels distributed via GitHub releases.

## Release Workflow

### Automated Triggers
- **Version Change**: Release only creates when `package.json` version differs from existing git tags
- **Main Branch**: Only releases from commits on the `main` branch

### Current Version
- **JavaScript Client**: v1.1.0
- **Python Client**: v1.1.0

## Creating a New Release
 
### 1. Version Update
Update the version in both configuration files:

**JavaScript** (`package.json`):
```json
{
  "version": "1.1.0"
}
```

**Python** (`pyproject.toml`):
```toml
[project]
version = "1.1.0"
```

### 2. Commit and Push
```bash
git add package.json pyproject.toml
git commit -m "Bump version to v1.1.0"
git push origin main
```

### 3. Automatic Processing
The GitHub Actions workflow will:
1. **Detect** the version change
2. **Build** JavaScript bundles and Python wheels
3. **Create** release branch with built files committed
4. **Create** git tag (e.g., `v1.1.0`) on the release branch
5. **Publish** GitHub release with attached assets

## Build Artifacts & Distribution

### JavaScript Distribution
Built files are created in `javascript/dist/` and committed to the release branch for CDN access:

**CDN URLs** (available via jsDelivr):
```
https://cdn.jsdelivr.net/gh/WAVE-Lab-Williams/wave-client@v1.0.0/javascript/dist/wave-client.esm.js
https://cdn.jsdelivr.net/gh/WAVE-Lab-Williams/wave-client@v1.0.0/javascript/dist/wave-client.umd.js
https://cdn.jsdelivr.net/gh/WAVE-Lab-Williams/wave-client@v1.0.0/javascript/dist/wave-client.umd.min.js
```

**Built Files**:
- `wave-client.esm.js` - ES6 module format (recommended)
- `wave-client.umd.js` - Universal module format
- `wave-client.umd.min.js` - Minified UMD build
- Source maps for all builds

**Usage in HTML**:
```html
<script type="module">
  import { WaveClient } from 'https://cdn.jsdelivr.net/gh/WAVE-Lab-Williams/wave-client@v1.0.0/javascript/dist/wave-client.esm.js';
  const client = new WaveClient({ apiKey: 'your-key' });
</script>
```

### Python Distribution  
Built files are created in standard `dist/` folder and distributed via GitHub releases:

**Installation Options**:
```bash
# Option 1: Install wheel from GitHub release assets (pip)
pip install https://github.com/WAVE-Lab-Williams/wave-client/releases/download/v1.0.0/wave_client-1.0.0-py3-none-any.whl

# Option 2: Install wheel from GitHub release assets (uv)
uv pip install https://github.com/WAVE-Lab-Williams/wave-client/releases/download/v1.0.0/wave_client-1.0.0-py3-none-any.whl

# Option 3: Install directly from GitHub repository (uv)
uv pip install git+https://github.com/WAVE-Lab-Williams/wave-client.git@v1.0.0
```

**Built Files**:
- `wave_client-{version}-py3-none-any.whl` - Python wheel package

## Release Assets

All built files are automatically attached to the GitHub release:
- **JavaScript**: All files from `javascript/dist/` (also committed to tag for CDN)
- **Python**: All `.whl` files from `dist/`
- **Release Notes**: Auto-generated from commit messages

## CDN Availability

### JavaScript Files
JavaScript builds are automatically available via CDN after release:

**jsDelivr CDN**:
- Updates within minutes of release
- Serves files directly from GitHub repository
- Global CDN with high availability

**Testing CDN Access**:
```bash
# Test if file is available
curl -I "https://cdn.jsdelivr.net/gh/WAVE-Lab-Williams/wave-client@v1.0.0/javascript/dist/wave-client.esm.js"

# Should return 200 OK
```

### Repository Structure
- **Development**: `javascript/dist/` is gitignored (clean repo)
- **Release Branch**: Built files committed to separate `release` branch for CDN access
- **Main Branch**: No built files (clean for developers)
- **Tags**: Created on release branch pointing to commits with built files

## Versioning Strategy

### Semantic Versioning
- **MAJOR.MINOR.PATCH** format (e.g., `1.2.3`)
- **Major**: Breaking changes (incompatible API changes)
- **Minor**: New features (backward compatible)
- **Patch**: Bug fixes (backward compatible)

### Compatibility Rules
- Same major version = compatible (e.g., 1.0.0 ↔ 1.5.2)
- Different major version = potentially incompatible (e.g., 1.x.x ↔ 2.x.x)
- Server validates compatibility via semantic versioning

### Version Synchronization
- Keep JavaScript and Python versions aligned when possible
- Both clients should increment together for coordinated releases
- Independent patches allowed for language-specific fixes

## Troubleshooting Releases

### Release Not Triggered
**Problem**: New version committed but no release created
**Solutions**:
1. Verify version in `package.json` is different from existing tags
2. Ensure commit is on `main` branch
3. Check GitHub Actions workflow logs for errors

### Build Failures
**Problem**: Release workflow fails during build
**Solutions**:
1. Check JavaScript build: `npm run build:prod` locally
2. Check Python build: `uv build` locally
3. Review workflow logs in GitHub Actions tab

### Missing Assets
**Problem**: Release created but files not attached
**Solutions**:
1. Check artifact upload steps in workflow logs
2. Verify build outputs are created correctly
3. Ensure file paths match expected locations

## Monitoring Releases

### GitHub Actions
- Navigate to **Actions** tab in GitHub repository
- Monitor **Release** workflow execution
- Check individual job logs for detailed output

### Release Verification
After release creation, verify:
1. **GitHub Release**: Check release page for attached assets
2. **jsDelivr CDN**: Test JavaScript file availability (may take 5-10 minutes)
3. **Python Wheel**: Test wheel file download and installation
4. **Tag Content**: Verify built files are present in the tagged commit

**CDN Verification Commands**:
```bash
# Check JavaScript CDN availability
curl "https://cdn.jsdelivr.net/gh/WAVE-Lab-Williams/wave-client@v1.0.0/javascript/dist/wave-client.esm.js"

# Check Python installation options
# Option 1: Test wheel download and pip installation
wget "https://github.com/WAVE-Lab-Williams/wave-client/releases/download/v1.0.0/wave_client-1.0.0-py3-none-any.whl"
pip install wave_client-1.0.0-py3-none-any.whl

# Option 2: Test wheel installation with uv
uv pip install https://github.com/WAVE-Lab-Williams/wave-client/releases/download/v1.0.0/wave_client-1.0.0-py3-none-any.whl

# Option 3: Test direct repository installation with uv
uv pip install git+https://github.com/WAVE-Lab-Williams/wave-client.git@v1.0.0
```

## Security Considerations

### Automated Process
- No manual intervention required after version bump
- Reduces human error in release process
- Consistent build environment via GitHub Actions

### Asset Integrity
- All builds happen in isolated GitHub runners
- Source code is immutable at time of release
- Release assets are cryptographically signed by GitHub

## Development Workflow Integration

### Pre-Release Testing
Before bumping version:
1. Run full test suite: `make test-all`
2. Verify local builds: `make build-js` and `uv build`
3. Test integration scenarios
4. Review changelog and breaking changes

### Post-Release Validation
After automatic release:
1. **Test JavaScript CDN URLs** in browser console
2. **Install and test Python wheel** locally
3. **Verify documentation** matches released version
4. **Test integration examples** with new CDN URLs
5. **Update dependent projects** to use new version

**JavaScript Testing**:
```html
<!-- Test in browser -->
<script type="module">
  import { WaveClient } from 'https://cdn.jsdelivr.net/gh/WAVE-Lab-Williams/wave-client@v1.1.0/javascript/dist/wave-client.esm.js';
  console.log('CDN test:', new WaveClient());
</script>
```

**Python Testing**:
```bash
# Option 1: Test wheel installation with pip
pip install wave_client-1.1.0-py3-none-any.whl
python -c "from wave_client import WaveClient; print('Wheel test (pip):', WaveClient)"

# Option 2: Test wheel installation with uv
uv pip install wave_client-1.1.0-py3-none-any.whl
python -c "from wave_client import WaveClient; print('Wheel test (uv):', WaveClient)"

# Option 3: Test direct repository installation with uv
uv pip install git+https://github.com/WAVE-Lab-Williams/wave-client.git@v1.1.0
python -c "from wave_client import WaveClient; print('Repository test (uv):', WaveClient)"
```

## Related Documentation

- [Installation Guide](./installation.md) - Setup instructions for end users
- [API Reference](./api-reference.md) - Complete API documentation