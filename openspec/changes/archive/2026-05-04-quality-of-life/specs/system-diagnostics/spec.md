## MODIFIED Requirements

### Requirement: Command Invocation Tracking
The system SHALL record detailed metadata for every external command executed (e.g., `makepkg`, `pacman`, `repo-add`), including arguments and environment. For commands executed within an isolated environment, the system SHALL provide a concise summary at the INFO level instead of the full host-side command string.

#### Scenario: Executing an external command on the host
- **GIVEN** an external tool like `git` is being called directly on the host
- **WHEN** the execution starts
- **THEN** the system SHALL log the full command, working directory, and any environment overrides at the INFO level

#### Scenario: Executing a sandboxed command
- **GIVEN** a command is being executed via Bubblewrap
- **WHEN** the execution starts
- **THEN** the system SHALL log a concise summary of the operation and environment (e.g., "Executing makepkg in sandbox [net: shared]") at the INFO level
- **AND** it SHALL log the full host-side `bwrap` command at the DEBUG level only
