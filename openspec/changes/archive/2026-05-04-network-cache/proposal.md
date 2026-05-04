## Why

The tool currently performs redundant network requests to AUR and PyPI during dependency resolution and maintenance audits. Caching these responses reduces network overhead, improves performance for repeated operations, and allows the tool to function (with stale data) in offline or spotty network conditions.

## What Changes

- Introduce a persistent JSON cache for AUR and PyPI metadata responses.
- Implement a 1-hour staleness threshold for cached data.
- Provide a fallback mechanism to use stale cache data if network updates fail.
- Organize cache storage into client-specific subdirectories under the workspace `srv/` directory.

## Capabilities

### New Capabilities
- `network-response-caching`: Manages the lifecycle, storage, and retrieval of external API responses with TTL enforcement and error fallback.

### Modified Capabilities
- `dependency-resolution`: Will now use the caching capability to retrieve AUR and PyPI metadata.
- `maintenance-management`: Will now use the caching capability to retrieve PyPI version information.

## Impact

- `aur_python_packer/clients.py`: Refactored to integrate with the new caching layer.
- `aur_python_packer/resolver.py`: Updated to pass caching context.
- `aur_python_packer/audit.py`: Updated to pass caching context.
- `aur_python_packer/main.py`: Orchestrates the initialization of the cache.
- Workspace structure: New `srv/network_cache/` directory.
