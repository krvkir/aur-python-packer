# Component: Rootless Isolated Build

## Purpose
Provides a secure, rootless build environment using Bubblewrap (bwrap). It isolates the build process from the host system, maps the current user to root within the container, and automatically manages a minimal Arch Linux root filesystem for hermetic builds without requiring host-level sudo privileges.

## Requirements

### Requirement: Rootless Isolated Build Environment
The system SHALL provide a build environment that uses `bwrap` (Bubblewrap) to isolate the process from the host system and run without `sudo`.

#### Scenario: Build in rootless sandbox
- **WHEN** a build is triggered
- **THEN** the system SHALL execute the build command inside a `bwrap` container.
- **AND** the container SHALL have the current user mapped to `uid 0` and `gid 0`.
- **AND** the container SHALL have the `work/root` directory bound to `/`.

### Requirement: Automated Root Bootstrapping
The system SHALL automatically initialize a minimal Arch Linux root filesystem in the `work` directory if it does not already exist.

#### Scenario: First-time build bootstrap
- **WHEN** a build starts and `work/root` is missing
- **THEN** the system SHALL run `pacman` with the `--root` flag to install `base-devel` into `work/root`.

### Requirement: Sudo Command Shim
The system SHALL provide a `sudo` executable within the build environment that allows `makepkg` to execute commands without requiring actual host-level `sudo`.

#### Scenario: Makepkg calls sudo
- **WHEN** `makepkg` invokes `sudo pacman` inside the `bwrap` sandbox
- **THEN** the shim SHALL intercept the call and execute `pacman` directly as the sandboxed root user.
