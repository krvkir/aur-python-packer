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

### Requirement: Workspace State Isolation
All persistent data and internal tool state SHALL be contained within the designated workspace directory.

#### Scenario: State file location
- **GIVEN** a workspace directory is set
- **WHEN** the system saves state
- **THEN** the state files MUST be stored inside the workspace directory (e.g., `work/state.json`)

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

## Implementation Notes
- CLI uses `--work-dir` (or `-w`) flag.
- State is stored in `state.json`.
- AUR cache is stored in `aur_cache/`.
- Default workspace is `work/`.
