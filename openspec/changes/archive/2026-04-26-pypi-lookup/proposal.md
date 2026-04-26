## Why

Currently, the system assumes any package starting with `python-` exists on PyPI and ignores its sub-dependencies, resulting in incomplete `PKGBUILD` files and potential resolution failures for packages not in repos/AUR. This change implements proper PyPI verification and recursive dependency extraction.

## What Changes

- **PyPI Verification**: Replace the current mock/placeholder with a real API request to verify package existence on PyPI.
- **Recursive Resolution**: Extract `requires_dist` from PyPI metadata and feed them back into the dependency resolver.
- **Dependency Parsing**: Integrate the `packaging` library to handle PEP 508 dependency strings and environment markers.
- **Standardized Mapping**: Consistent mapping between PyPI names (e.g., `FastMCP`) and Arch names (e.g., `python-fastmcp`) throughout the build process.

## Capabilities

### New Capabilities
- `pypi-lookup`: Verifies package existence on PyPI and retrieves detailed metadata including dependencies.

### Modified Capabilities
- `dependency-resolver`: Incorporates recursive dependency discovery for packages identified as PyPI-sourced.
- `package-generator`: Includes resolved sub-dependencies in the generated `PKGBUILD` `depends` array.

## Impact

- **Codebase**: `DependencyResolver` and `PyPIGenerator` will require significant updates.
- **Dependencies**: Add `packaging` to `pyproject.toml`.
- **System**: Increased reliability of generated packages by ensuring all transitive dependencies are identified and resolved.
