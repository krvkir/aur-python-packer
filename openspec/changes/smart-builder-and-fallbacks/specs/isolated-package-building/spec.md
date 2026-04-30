# Capability: Isolated Package Building (Refinement)

## Requirements

### Requirement: Automated Build Fallback
The system SHALL automatically attempt to rebuild a package with tests disabled if a standard build attempt fails for any reason.

#### Scenario: Fallback to --nocheck
- **GIVEN** a package build is initiated with tests enabled
- **WHEN** the initial build fails
- **THEN** the system SHALL immediately trigger a second build attempt with the `--nocheck` flag.

### Requirement: Detailed Build Status Tracking
The system SHALL record the specific conditions under which a package was successfully built, particularly whether tests were skipped.

#### Scenario: Tracking skipped checks
- **GIVEN** a package was successfully built with the `--nocheck` flag
- **WHEN** the build index is updated
- **THEN** the entry for the package MUST include a `skipped_checks: true` field.

#### Scenario: Tracking global skip
- **GIVEN** the build was launched with the global `--nocheck` option
- **WHEN** any package is successfully built
- **THEN** it MUST be marked as `skipped_checks: true` in the index.
