# WAVE Client Release Process

## Overview

The WAVE Client uses a fully automated release system that builds and distributes both JavaScript and Python clients whenever a new version is detected on the main branch.

## Release Workflow

### Automated Triggers
- **CI Success**: Release only runs after all CI workflows (JavaScript CI, Python CI, Integration Tests) pass
- **Version Change**: Release only creates when `package.json` version differs from existing git tags
- **Main Branch**: Only releases from commits on the `main` branch

### Current Version
- **JavaScript Client**: v1.0.0
- **Python Client**: v1.0.0

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
2. **Wait** for all CI tests to pass
3. **Create** git tag (e.g., `v1.1.0`)
4. **Build** JavaScript bundles and Python wheels
5. **Publish** GitHub release with attached assets

## Build Artifacts

### JavaScript Distribution
Built files are created in `javascript/dist/`:
- `wave-client.esm.js` - ES6 module format
- `wave-client.umd.js` - Universal module format
- `wave-client.umd.min.js` - Minified UMD build
- Source maps for all builds

### Python Distribution  
Built files are created in `dist/`:
- `wave_client-{version}-py3-none-any.whl` - Python wheel package

## Release Assets

All built files are automatically attached to the GitHub release:
- **JavaScript**: All files from `javascript/dist/`
- **Python**: All `.whl` files from `dist/`
- **Release Notes**: Auto-generated from commit messages

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
1. Check that CI workflows passed successfully
2. Verify version in `package.json` is different from existing tags
3. Ensure commit is on `main` branch

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
2. **jsDelivr CDN**: Test JavaScript file availability
3. **Python Wheel**: Test wheel file download and installation

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
1. Test JavaScript CDN URLs in browser
2. Install and test Python wheel
3. Verify documentation matches released version
4. Update any dependent projects

## Related Documentation

- [Installation Guide](./installation.md) - Setup instructions for end users
- [API Reference](./api-reference.md) - Complete API documentation