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
The system SHALL generate a valid `PKGBUILD` file using a standardized Jinja2 template and subsequently generate `.SRCINFO` using native Arch Linux tools.

#### Scenario: Generate for new package
- **GIVEN** metadata has been retrieved for a package
- **WHEN** generating artifacts
- **THEN** the system SHALL render a `PKGBUILD` from a template
- **AND** it SHALL execute `makepkg --printsrcinfo` to generate the corresponding `.SRCINFO` file

### Requirement: Automated Checksum Verification
The system SHALL utilize native Arch Linux tools to calculate and verify source checksums.

#### Scenario: Source checksum calculation
- **GIVEN** a `PKGBUILD` has been generated
- **WHEN** the system triggers checksum verification
- **THEN** it SHALL execute `updpkgsums` within the isolated build environment to update the `PKGBUILD` with correct hashes.

### Requirement: Dependency Mapping
The system SHALL parse PyPI dependency specifications and map them to Arch Linux package naming conventions using an authoritative mapping configuration.

#### Scenario: Map external dependency
- **GIVEN** a PyPI dependency string (e.g., `requests >= 2.21.0`)
- **WHEN** parsing the requirement
- **THEN** it SHALL use the mapping configuration to determine the corresponding Arch package name (e.g., `python-requests>=2.21.0`)

## Implementation Notes
- Uses the PyPI JSON API for metadata retrieval.
- Extracts `requires_dist` from PyPI metadata.
- Generates `PKGBUILD` using an external Jinja2 template.
- Uses `updpkgsums` to update checksums in the `PKGBUILD`.
- Uses `makepkg --printsrcinfo` to generate `.SRCINFO`.
- Uses `pypi_mapping.json` as the authoritative source for name translations.
