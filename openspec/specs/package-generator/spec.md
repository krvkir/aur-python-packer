# Component: Package Generator

## Purpose
Automates the creation of Arch Linux packaging files for Python-based software. It queries the PyPI JSON API to retrieve metadata and uses standardized templates to generate `PKGBUILD` and `.SRCINFO` files, including automated source fetching and checksum verification.

## Requirements

### Requirement: PyPI Metadata Fetching
The system SHALL be able to retrieve package version, license, and dependency information from the PyPI JSON API for any given package name.

#### Scenario: Successful metadata retrieval
- **WHEN** the system queries PyPI for `python-requests`
- **THEN** it SHALL extract the latest version string and the list of `requires_dist`.

### Requirement: PKGBUILD Generation
The system SHALL generate a valid Arch Linux `PKGBUILD` and `.SRCINFO` for a Python package using a standardized template.

#### Scenario: Generate for new package
- **WHEN** a dependency is only found on PyPI
- **THEN** the system SHALL create a directory with a PKGBUILD containing correct `pkgname`, `pkgver`, `depends`, and checksums.

#### Scenario: Handle checksums
- **WHEN** generating a PKGBUILD
- **THEN** the system SHALL download the source tarball and calculate the SHA256 sum automatically.
