## MODIFIED Requirements

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
  - `work/srv/home/`: For the sandboxed user home directory.
  - `work/pypi_mapping.json`: For dependency name mapping.

### Requirement: Dependency Graph Visualization
The system SHALL provide a graphical representation of the dependency DAG (Directed Acyclic Graph) to allow users to visualize complex relationships and build status during the resolution process. To prevent terminal clutter, repository-tier dependencies SHALL be omitted from large graphs by default.

#### Scenario: Visualizing small dependency DAG
- **GIVEN** a dependency graph with 20 or fewer total nodes
- **WHEN** the user resolves dependencies or builds a package
- **THEN** the system SHALL output a complete DAG visualization including all tiers

#### Scenario: Visualizing large dependency DAG
- **GIVEN** a dependency graph with more than 20 total nodes
- **WHEN** the user resolves dependencies or builds a package
- **THEN** the system SHALL omit nodes belonging to the "repo" (official repositories) tier from the visualization
- **AND** it SHALL display a notice indicating the number of omitted dependencies

#### Scenario: Visualizing large dependency DAG with override
- **GIVEN** a dependency graph with more than 20 total nodes
- **AND** the `--show-repo-deps` flag is provided
- **WHEN** the user resolves dependencies or builds a package
- **THEN** the system SHALL output a complete DAG visualization including all repository dependencies

### Requirement: Package Source Version Control
The system SHALL provide built-in Git integration to track manual modifications to package source files using the `git` tool available in the chroot environment.

#### Scenario: Initialize tracking with host identity
- **WHEN** the `git-init` command is executed
- **THEN** the system SHALL initialize Git repositories in all directories within `packages/` and `aur_packages/` if they are not already repositories
- **AND** it SHALL configure the repository `user.name` and `user.email` using the values from the host system's global Git configuration

#### Scenario: Identify manual changes with streaming output
- **WHEN** the `git-show` command is executed
- **THEN** the system SHALL identify package directories containing uncommitted changes to the `PKGBUILD`
- **AND** it SHALL print each identified package to the terminal immediately upon discovery rather than waiting for the entire scan to complete
