## MODIFIED Requirements

### Requirement: PyPI Metadata Fetching
The system SHALL be able to retrieve package version, license, and dependency information from the PyPI JSON API for any given package name.

#### Scenario: Successful metadata retrieval
- **WHEN** the system queries PyPI for a project name (e.g., `fastmcp`)
- **THEN** it SHALL extract the latest version string and the list of `requires_dist`.

### Requirement: PKGBUILD Generation
The system SHALL generate a valid Arch Linux `PKGBUILD` and `.SRCINFO` for a Python package using a standardized template.

#### Scenario: Generate for new package
- **WHEN** a dependency is only found on PyPI
- **THEN** the system SHALL create a directory named after the Arch package (e.g., `python-fastmcp`) with a PKGBUILD containing correct `pkgname`, `pkgver`, `depends`, and checksums.

#### Scenario: Handle checksums
- **WHEN** generating a PKGBUILD
- **THEN** the system SHALL download the source tarball and calculate the SHA256 sum automatically.

## ADDED Requirements

### Requirement: Dependency Parsing and Mapping
The system SHALL parse PEP 508 dependency strings and map them to Arch Linux package names.

#### Scenario: Map PyPI dependency to Arch
- **WHEN** the system parses a requirement `requests >= 2.21.0`
- **THEN** it SHALL map it to the Arch package name `python-requests`.
