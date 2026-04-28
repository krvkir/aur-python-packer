# Capability: Package Generation

## Purpose
Automates the creation of package metadata and build instructions based on information retrieved from external software indices.

## Requirements

### Requirement: External Metadata Retrieval
The system SHALL retrieve software version, license, and dependency information using the PyPI JSON API.

#### Scenario: Successful metadata retrieval
- **GIVEN** a target Python package name (e.g., `requests`)
- **WHEN** the system queries the PyPI JSON API
- **THEN** it SHALL extract the latest version, license, and the list of `requires_dist` dependencies

### Requirement: Packaging Artifact Generation
The system SHALL generate valid `PKGBUILD` and `.SRCINFO` files using standardized Jinja2 templates.

#### Scenario: Generate for new package
- **GIVEN** metadata has been retrieved for a package
- **WHEN** generating artifacts
- **THEN** the system SHALL create a package directory containing a `PKGBUILD` and a `.SRCINFO` file

### Requirement: Automated Checksum Verification
The system SHALL automatically download source tarballs and calculate SHA256 checksums.

#### Scenario: Source checksum calculation
- **GIVEN** a package is being generated
- **WHEN** the system downloads the source tarball from PyPI
- **THEN** it SHALL calculate the SHA256 hash and include it in the `sha256sums` array of the `PKGBUILD`

### Requirement: Dependency Mapping
The system SHALL parse PyPI dependency specifications and map them to Arch Linux package naming conventions.

#### Scenario: Map external dependency
- **GIVEN** a PyPI dependency string (e.g., `requests >= 2.21.0`)
- **WHEN** parsing the requirement
- **THEN** it SHALL be mapped to the corresponding Arch package name (e.g., `python-requests>=2.21.0`)

## Implementation Notes
- Uses the PyPI JSON API for metadata retrieval.
- Extracts `requires_dist` from PyPI metadata.
- Generates `PKGBUILD` and `.SRCINFO` files.
- Uses `updpkgsums` or equivalent logic for checksums.
