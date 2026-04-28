## ADDED Requirements

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
