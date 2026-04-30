# Capability: Local Repository Management

## Purpose
Manages a local repository of built packages to satisfy dependencies during the build process of subsequent packages.

## Requirements

### Requirement: Local Repository Maintenance
The system SHALL maintain a local `pacman` package repository within the `local_repo/` subdirectory of the workspace.

#### Scenario: Add package to repository
- **GIVEN** a package has been successfully built (e.g., `python-foo-1.0.0-1-any.pkg.tar.zst`)
- **WHEN** the system processes the artifact
- **THEN** it SHALL move the `.pkg.tar.zst` file to `work/local_repo/`
- **AND** it SHALL update the repository database in that same directory.

### Requirement: Build Environment Integration
The system SHALL configure build environments to trust and utilize the local repository as a source for dependencies.

#### Scenario: Repository configuration
- **GIVEN** a build environment is being prepared
- **WHEN** configuring the package manager
- **THEN** the system SHALL add the local repository as a trusted source

### Requirement: Modern Package Manager Compatibility
The system SHALL ensure the local repository and the package manager configuration are compatible with modern `pacman` versions (7.1+) when running in isolated environments.

#### Scenario: Running with modern pacman
- **GIVEN** a build environment with `pacman` 7.1+
- **WHEN** initializing the configuration
- **THEN** the system SHALL apply necessary overrides (e.g., `DownloadUser`, `XferCommand`) to ensure network operations and database synchronization work correctly in rootless isolation.

## Implementation Notes
- Uses `repo-add` to manage the repository database.
- Modifies `pacman.conf` in the build environment.
- Sets `SigLevel = Optional TrustAll` for the local repository.
- Applies `DownloadUser = root` and custom `XferCommand` overrides for Pacman 7.1 compatibility.
