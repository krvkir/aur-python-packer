# Capability: Project Constraints

## Purpose
Defines the fundamental structural and environment requirements for the project itself to ensure consistency and maintainability.

## Requirements

### Requirement: Standardized Repository Layout
The project SHALL follow a consistent directory structure for source code, tests, and configuration.

#### Scenario: Structure verification
- **GIVEN** the project repository
- **WHEN** inspecting the root directory
- **THEN** the primary configuration, source directory, and test directory MUST be present in standardized locations
+ **THEN** `pyproject.toml` SHALL be at the root
+ **AND** `aur_python_packer/` directory SHALL be at the root
+ **AND** `tests/` directory SHALL be at the root

### Requirement: Formal Dependency Management
The project SHALL use Poetry for managing its own development and runtime dependencies.

#### Scenario: Managing dependencies
- **GIVEN** the project source code
- **WHEN** installing or updating dependencies
- **THEN** the system SHALL use `poetry install` or `poetry add` to ensure environment consistency

### Requirement: Consistent Package Identification
The project's primary software package SHALL be named `aur_python_packer`.

#### Scenario: Package identification
- **GIVEN** the source code
- **WHEN** identifying the package for import or distribution
- **THEN** it SHALL use the name `aur_python_packer`

## Implementation Notes
- Uses Poetry for dependency management.
- Configuration is in `pyproject.toml`.
- Package name is `aur_python_packer`.
- Source code is in `src/`, tests in `tests/`.
+ Source code is in `aur_python_packer/`, tests in `tests/`.
