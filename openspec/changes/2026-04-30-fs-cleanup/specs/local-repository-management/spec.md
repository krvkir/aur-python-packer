# Capability: Local Repository Management (Refinement)

## Requirements

### Requirement: Local Repository Maintenance (Updated)
The system SHALL maintain a local `pacman` package repository within the `local_repo/` subdirectory of the workspace.

#### Scenario: Add package to repository
- **GIVEN** a package has been successfully built
- **WHEN** the system processes the artifact
- **THEN** it SHALL move the `.pkg.tar.zst` file to `work/local_repo/`
- **AND** it SHALL update the repository database in that same directory.
