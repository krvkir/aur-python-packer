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

## Implementation Notes
- CLI uses `--work-dir` (or `-w`) flag.
- State is stored in `state.json`.
- AUR cache is stored in `aur_cache/`.
- Default workspace is `work/`.
