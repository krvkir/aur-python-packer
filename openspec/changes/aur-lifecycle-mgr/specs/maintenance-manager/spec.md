## ADDED Requirements

### Requirement: Version Auditing
The system SHALL compare the versions of locally managed packages against the latest available versions on PyPI.

#### Scenario: Identify outdated packages
- **WHEN** the local `python-foo` is at version 1.0.0 and PyPI has 1.1.0
- **THEN** the system SHALL mark the package as "Outdated" in the audit report.

### Requirement: Automated Update Triggering
The system SHALL allow updating an outdated package by bumping its `pkgver` and regenerating checksums.

#### Scenario: Update package version
- **WHEN** a user triggers an update for an outdated package
- **THEN** the system SHALL update the `PKGBUILD` file, run `updpkgsums`, and queue it for a rebuild.
