# Component: Chroot Builder

## Purpose
Orchestrates the package build process and verifies build success. It leverages the isolated build environment to produce package files and updates the build index with the results, ensuring builds are hermetic and repeatable.

## Requirements

### Requirement: Build Success Verification
The system SHALL verify that a build produced the expected `.pkg.tar.zst` file and mark the build as successful in the state tracker. It SHALL log the build progress to the log file and provide high-level status to the terminal.

#### Scenario: Successful build tracking
- **WHEN** a build command exits with status 0 and a package file is created
- **THEN** the system SHALL update the `build_index.json` with the new status and version.
- **THEN** the full build log MUST be available in the session log file.
