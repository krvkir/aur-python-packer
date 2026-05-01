# Capability: User Interaction Interface

## Purpose
Provides the primary interface for users to configure the tool and initiate packaging and build operations.

## Requirements

### Requirement: Configurable Workspace Location
The system SHALL allow the user to specify a custom directory for storing state, AUR cache, and the local repository.

#### Scenario: Custom workspace provided
- **GIVEN** a user-specified path (e.g., `/var/lib/aur-packer`)
- **WHEN** the tool is initialized
- **THEN** the system SHALL use that path as the root for all persistent data (state, cache, logs, local repo)

### Requirement: Rigid Workspace Structure
The system SHALL organize the workspace directory into a standardized set of subdirectories to separate source code, build artifacts, logs, and internal state.

#### Scenario: Workspace initialization
- **GIVEN** a workspace directory `work/`
- **WHEN** the tool is initialized
- **THEN** it SHALL ensure the following structure exists:
  - `work/aur_packages/`: For AUR source clones.
  - `work/packages/`: For PyPI generated packages.
  - `work/local_repo/`: For the pacman repository database and built packages.
  - `work/logs/`: For diagnostic logs.
  - `work/srv/`: For internal tool state and the build sandbox.
  - `work/pypi_mapping.json`: For dependency name mapping.

### Requirement: Workspace State Isolation
All persistent internal data and internal tool state SHALL be contained within the `srv/` subdirectory of the designated workspace.

#### Scenario: State file location
- **GIVEN** a workspace directory is set
- **WHEN** the system saves state
- **THEN** the state files MUST be stored inside the `srv/` directory (e.g., `work/srv/build_index.json`).

### Requirement: Session Diagnostic Visibility
The system SHALL provide the user with clear information about the location of diagnostic logs for the current session.

#### Scenario: Log path notification
- **GIVEN** the tool starts
- **WHEN** a new session is initialized
- **THEN** it SHALL display a notification like `Logs: logs/run_20231027_103000.log` to the user

### Requirement: Dependency Graph Visualization
The system SHALL provide a graphical representation of the dependency DAG (Directed Acyclic Graph) to allow users to visualize complex relationships and build status during the resolution process.

#### Scenario: Visualizing dependency DAG
- **GIVEN** a package with dependencies
- **WHEN** the user resolves dependencies
- **THEN** the system SHALL output an ASCII/Unicode DAG visualization
- **AND** it SHALL highlight nodes that are already successfully built
- **AND** it SHALL support ANSI colors in interactive terminals while ensuring they are stripped for non-TTY output

### Requirement: Real-time Build Progress Visualization
The system SHALL display the dependency graph during the build process to provide real-time updates on progress and status.

#### Scenario: Graph display in build loop
- **GIVEN** a build process for multiple packages
- **WHEN** the build starts
- **THEN** the system SHALL display the initial dependency graph
- **WHEN** a package is successfully built
- **THEN** the system SHALL redisplay the graph with the updated status for that package

### Requirement: Graceful Resolution Failure Reporting
The system SHALL gracefully report when a package or its dependencies cannot be resolved, providing a clear error message instead of an uncaught exception.

#### Scenario: Package not found
- **GIVEN** a package name that does not exist in local, repo, AUR, or PyPI
- **WHEN** the user attempts to resolve or build the package
- **THEN** the system SHALL report "Could not resolve dependency: <pkgname>" and exit cleanly


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
## Implementation Notes
- CLI uses `--work-dir` (or `-w`) flag.
- State is stored in `srv/build_index.json`.
- AUR cache is stored in `aur_packages/`.
- Default workspace is `work/`.
