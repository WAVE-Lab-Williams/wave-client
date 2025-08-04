"""
Versioning utilities for client-server compatibility.

This module provides lightweight version compatibility checking between WAVE client
libraries (Python & JavaScript) and the backend API. It uses HTTP headers to
communicate version information and provides non-blocking compatibility warnings.

## How Version Compatibility Works

1. **Client Headers**: Clients send X-WAVE-Client-Version header with requests
2. **Server Response**: Server adds X-WAVE-API-Version header to all responses
3. **Compatibility Check**: Server logs warnings for incompatible combinations
4. **Non-blocking**: Incompatible versions get warnings, not errors

## Semantic Versioning Compatibility Rules

This system uses standard semantic versioning (semver) compatibility rules:

- **Same major version = Compatible**: 1.0.0 ↔ 1.5.0 ✅
- **Different major version = Incompatible**: 1.0.0 ↔ 2.0.0 ❌
- **Backward compatibility**: Newer minor/patch versions work with older ones
- **Forward compatibility**: Older clients work with newer API minor/patch versions

### Examples:
- Client 1.0.0 + API 1.0.1 = ✅ Compatible (patch update)
- Client 1.2.0 + API 1.5.0 = ✅ Compatible (minor updates, same major)
- Client 1.0.0 + API 2.0.0 = ❌ Incompatible (major version change)
- Client 2.1.0 + API 1.9.0 = ❌ Incompatible (different majors)

### Warning System
- `get_compatibility_warning()`: Returns warning text for incompatible versions
- `log_version_info()`: Logs compatibility status for monitoring
- Warnings are logged but don't block requests (graceful degradation)

## Version Update Strategy
1. **Patch updates** (1.0.0 → 1.0.1): Bug fixes, always compatible
2. **Minor updates** (1.0.0 → 1.1.0): New features, backward compatible
3. **Major updates** (1.0.0 → 2.0.0): Breaking changes, update both client and API
"""

import logging
import re
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


def parse_version(version_string: str) -> Optional[Tuple[int, int, int]]:
    """
    Parse semantic version string into major, minor, patch tuple.

    Args:
        version_string: Version string like "1.2.3" or "v1.2.3"

    Returns:
        Tuple of (major, minor, patch) or None if invalid
    """
    if not version_string:
        return None

    # Remove 'v' prefix if present
    version_string = version_string.lstrip("v")

    # Match semantic version pattern
    pattern = r"^(\d+)\.(\d+)\.(\d+)(?:-.*)?(?:\+.*)?$"
    match = re.match(pattern, version_string)

    if not match:
        return None

    try:
        major, minor, patch = map(int, match.groups())
        return (major, minor, patch)
    except ValueError:
        return None


def is_compatible(client_version: str, api_version: str) -> bool:
    """
    Check if client and API versions are compatible.

    Uses semantic versioning rules: same major version = compatible.

    Args:
        client_version: Client version string
        api_version: API version string

    Returns:
        True if versions are compatible, False otherwise
    """
    client_parsed = parse_version(client_version)
    api_parsed = parse_version(api_version)

    # If we can't parse either version, assume compatible (graceful degradation)
    if not client_parsed or not api_parsed:
        return True

    # Same major version = compatible
    return client_parsed[0] == api_parsed[0]


def get_compatibility_warning(client_version: str, api_version: str) -> Optional[str]:
    """
    Get warning message for incompatible versions.

    Args:
        client_version: Client version string
        api_version: API version string

    Returns:
        Warning message if incompatible, None if compatible
    """
    if is_compatible(client_version, api_version):
        return None

    client_parsed = parse_version(client_version)
    api_parsed = parse_version(api_version)

    if not client_parsed or not api_parsed:
        return f"Version compatibility check failed - Client: {client_version}, API: {api_version}"

    client_major = client_parsed[0]
    api_major = api_parsed[0]

    if client_major > api_major:
        return (
            f"Client version {client_version} is newer than API version {api_version}. "
            f"Consider updating the API or downgrading the client for full compatibility."
        )
    else:
        return (
            f"Client version {client_version} is older than API version {api_version}. "
            f"Consider updating the client for access to newer features and bug fixes."
        )


def log_version_info(client_version: str, api_version: Optional[str] = None):
    """
    Log version compatibility information.

    Args:
        client_version: Client version string
        api_version: API version string (optional)
    """
    if not api_version:
        logger.info(f"WAVE Client version: {client_version}")
        return

    compatible = is_compatible(client_version, api_version)
    warning = get_compatibility_warning(client_version, api_version)

    if compatible:
        logger.info(f"Version compatibility ✅ - Client: {client_version}, API: {api_version}")
    else:
        logger.warning(f"Version compatibility ⚠️  - Client: {client_version}, API: {api_version}")
        if warning:
            logger.warning(f"Compatibility warning: {warning}")


def get_client_version() -> str:
    """
    Get the current client version.

    Returns:
        Client version string
    """
    # Import here to avoid circular imports
    from wave_client import __version__

    return __version__
