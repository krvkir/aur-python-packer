## Why

Manually parsing PKGBUILD files and their dependencies for a complex software stack like JupyterAI is tedious and error-prone. To automate clean-room builds (e.g., using `makechrootpkg`), we first need a reliable way to discover all local packages and their metadata to construct a valid build order and resolve missing dependencies.

## What Changes

- Implement a recursive scanner that traverses a target directory to locate all `PKGBUILD` files.
- Develop a parser to extract critical metadata (`pkgname`, `pkgver`, `depends`, `makedepends`, `checkdepends`) from discovered `PKGBUILD`s.
- Provide a structured output (mapping `pkgname` to its location and dependencies) to be used by subsequent resolution and build steps.

## Capabilities

### New Capabilities
- `package-discovery`: Recursively scan directories for `PKGBUILD` files and group them by package name.
- `metadata-parsing`: Extract dependency lists and version information from PKGBUILD bash scripts.

### Modified Capabilities
None.

## Impact

This component serves as the data foundation for the AUR build orchestrator. It will impact how local packages are identified and how the dependency resolver determines which packages are available locally versus needing to be fetched from the AUR or official repositories.
