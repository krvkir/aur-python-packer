# Capability: System Diagnostics

## Purpose
Provides comprehensive logging and diagnostic capabilities to monitor tool execution, capture command outputs, and facilitate troubleshooting of build failures.
## Requirements
### Requirement: Dual-Output Logging
The system SHALL support concurrent logging to both the terminal for user feedback and a persistent file for detailed diagnostics, using human-readable formats in the terminal.

#### Scenario: INFO level terminal logging
- **GIVEN** the application is running
- **WHEN** an INFO level log message is generated
- **THEN** only the message content MUST appear on the terminal (no preamble)
- **AND** the full diagnostic preamble (timestamp, level, name) MUST be written to the log file

#### Scenario: WARNING and above level terminal logging
- **GIVEN** the application is running
- **WHEN** a WARNING, ERROR, or CRITICAL level log message is generated
- **THEN** the message MUST appear on the terminal with a minimal preamble `[LEVEL] Name: message`
- **AND** the full diagnostic preamble (timestamp, level, name) MUST be written to the log file

### Requirement: Automatic Log Management
The system SHALL ensure the necessary logging infrastructure exists and manage log files automatically.

#### Scenario: Log directory initialization
- **GIVEN** the application starts
- **WHEN** the log storage directory is missing
- **THEN** the system MUST create it automatically

### Requirement: Command Invocation Tracking
The system SHALL record detailed metadata for every external command executed (e.g., `makepkg`, `pacman`, `repo-add`), including arguments and environment.

#### Scenario: Executing an external command
- **GIVEN** an external tool like `makepkg` is being called
- **WHEN** the execution starts
- **THEN** the system SHALL log the full command, working directory, and any environment overrides

### Requirement: Merged Output Capture
The system SHALL capture and interleave the standard output and standard error streams of external commands.

#### Scenario: Capturing command output
- **GIVEN** an external command is running
- **WHEN** it produces output or errors
- **THEN** the system MUST capture these in real-time and write them to the diagnostic log

## Implementation Notes
- Logs are stored in the `logs/` directory within the configured workspace.
- Log files follow the `run_YYYYMMDD_HHMMSS.log` format.
- Uses `DEBUG` level for file logs and `INFO` level for terminal.
- Captures `subprocess` metadata (commands, CWD, env).
- Uses level-dependent formatting for terminal output to ensure clean progress messages.
