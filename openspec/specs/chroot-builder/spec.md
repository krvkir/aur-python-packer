# Component: Chroot Builder

## Purpose
Provides a distro-aware build isolation layer. It detects whether the host is running Arch Linux or Manjaro and executes the appropriate native tool (`extra-x86_64-build` or `buildpkg`) to build packages in a clean chroot environment, ensuring builds are hermetic and repeatable.

## Requirements

### Requirement: Distro-Aware Build Orchestration
The system SHALL detect the host operating system (Arch or Manjaro) and use the appropriate chroot build tool.

#### Scenario: Build on Arch Linux
- **WHEN** the host is Arch Linux
- **THEN** the system SHALL execute `extra-x86_64-build` (from `devtools`) to perform the build.

#### Scenario: Build on Manjaro
- **WHEN** the host is Manjaro
- **THEN** the system SHALL execute `buildpkg` (from `manjaro-tools`) or a compatible chroot wrapper.

### Requirement: Build Success Verification
The system SHALL verify that a build produced the expected `.pkg.tar.zst` file and mark the build as successful in the state tracker.

#### Scenario: Successful build tracking
- **WHEN** a build command exits with status 0 and a package file is created
- **THEN** the system SHALL update the `build_state.json` with the new timestamp and version.

### Requirement: Default Chroot Build
The `Builder` SHALL use chroot-based build tools by default based on the detected host operating system.
- On Arch Linux, it SHALL use `extra-x86_64-build`.
- On Manjaro, it SHALL use `buildpkg`.

#### Scenario: Arch Linux default build
- **WHEN** the host is Arch Linux
- **THEN** the `Builder` executes `extra-x86_64-build`

#### Scenario: Manjaro default build
- **WHEN** the host is Manjaro
- **THEN** the `Builder` executes `buildpkg`

### Requirement: Chroot Tool Presence Check
The `Builder` SHALL verify that the required chroot build tools are installed and available in the system PATH before attempting a build.

#### Scenario: Chroot tools missing
- **WHEN** the required chroot tool is not found in PATH
- **THEN** the `Builder` SHALL raise an error and abort the build process

### Requirement: Local Build Fallback
The `Builder` SHALL support a local build mode using `makepkg` when explicitly requested via a flag, bypassing chroot tool checks and execution.

#### Scenario: Explicit local build
- **WHEN** the `--local` flag is provided to the CLI
- **THEN** the `Builder` executes `makepkg` instead of chroot tools
