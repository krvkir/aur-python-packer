# Capability: User Interaction Interface (Refinement)

## Requirements

### Requirement: Package Source Version Control
The system SHALL provide built-in Git integration to track manual modifications to package source files using the `git` tool available in the chroot environment.

#### Scenario: Initialize tracking
- **WHEN** the `git-init` command is executed
- **THEN** the system SHALL initialize Git repositories in all directories within `packages/` and `aur_packages/` if they are not already repositories.

#### Scenario: Identify manual changes
- **WHEN** the `git-show` command is executed
- **THEN** the system SHALL list all package directories containing uncommitted changes to the `PKGBUILD`.

### Requirement: Flexible Dependency Injection
The system SHALL allow users to explicitly add dependencies to a package build at runtime without modifying the `PKGBUILD` source.

#### Scenario: Inject dependency
- **GIVEN** a target package
- **WHEN** the build is launched with `-d <depname>` (one or more times)
- **THEN** the system SHALL add these dependencies to the package's resolution graph.
- **AND** it SHALL ensure they are built or installed before the target package.
