# Capability: User Interaction Interface (Refinement)

## Requirements

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

### Requirement: Workspace State Isolation (Updated)
All persistent internal data and internal tool state SHALL be contained within the `srv/` subdirectory of the designated workspace.

#### Scenario: State file location
- **GIVEN** a workspace directory is set
- **WHEN** the system saves state
- **THEN** the state files MUST be stored inside the `srv/` directory (e.g., `work/srv/build_index.json`).
