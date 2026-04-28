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

## Implementation Notes
- Uses `bwrap` (Bubblewrap) for rootless isolation.
- Maps current user to `uid 0` and `gid 0` within the container.
- Build root is stored in `work/root`.
- Bootstrapping is performed using `pacman --root` to install `base-devel`.
- A `sudo` shim is used to intercept calls and run them as the sandboxed root user.
- Status is tracked in `build_index.json`.
