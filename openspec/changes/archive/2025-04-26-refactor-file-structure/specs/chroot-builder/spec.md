## ADDED Requirements

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
