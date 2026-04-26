## ADDED Requirements

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
