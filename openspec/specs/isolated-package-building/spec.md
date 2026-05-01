# Capability: Isolated Package Building

## Purpose
Provides a secure and isolated environment for building packages, ensuring that the host system remains unaffected and that builds are hermetic and repeatable.

## Requirements

### Requirement: Isolated Sandbox Environment
The system SHALL execute builds within a sandbox that is isolated from the host operating system.

#### Scenario: Build in isolated sandbox
- **GIVEN** a package needs to be built
- **WHEN** the build process is initiated
- **THEN** the build MUST run inside an isolated container environment

### Requirement: Automated Environment Bootstrapping
The system SHALL automatically initialize the necessary build environment if it is missing.

#### Scenario: Environment initialization
- **GIVEN** a build is requested
- **AND** the build environment filesystem does not exist
- **WHEN** the builder starts
- **THEN** the system SHALL bootstrap a minimal Arch Linux root filesystem automatically

### Requirement: Privilege Elevation Simulation
The system SHALL provide a mechanism to allow build tools to perform administrative tasks within the sandbox without requiring host-level privileges.

#### Scenario: Tool requires administrative access
- **GIVEN** `makepkg` needs to install a dependency inside the sandbox
- **WHEN** it attempts to call `sudo pacman -U`
- **THEN** the system SHALL intercept and execute the command as a privileged user within the sandbox

### Requirement: Build Verification and Tracking
The system SHALL verify the success of the build process and maintain a record of build artifacts and status.

#### Scenario: Successful build tracking
- **GIVEN** a build has completed
- **WHEN** the process exits successfully and artifacts are generated
- **THEN** the system SHALL update the build index with the new status and version

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

## Implementation Notes
- Uses `bwrap` (Bubblewrap) for rootless isolation.
- Maps current user to `uid 0` and `gid 0` within the container.
+ Maps current user to their actual host UID/GID within the container (to satisfy `makepkg`).
- Build root is stored in `work/root`.
- Bootstrapping is performed using `pacman --root` to install `base-devel`.
- A `sudo` shim is used to intercept calls and run them as the sandboxed root user.
- Status is tracked in `build_index.json`.
