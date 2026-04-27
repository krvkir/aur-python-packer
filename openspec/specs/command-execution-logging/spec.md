# Component: Command Execution Logging

## Purpose
A specialized wrapper for external command execution that captures merged stdout/stderr streams in real-time, logs invocation metadata (commands, CWD, environment overrides), and provides detailed failure diagnostics.

## Requirements

### Requirement: Command invocation logging
The system SHALL log the full command, working directory, and environment overrides before execution.

#### Scenario: Executing a command
- **WHEN** an external tool like `makepkg` is called
- **THEN** the log file MUST contain the exact command list, the `cwd` used, and any specific environment variables added

### Requirement: Merged output capture
The system SHALL capture and log both standard output (stdout) and standard error (stderr) of external commands as a single interleaved stream.

#### Scenario: Command output logging
- **WHEN** an external command produces output or errors
- **THEN** the system MUST capture these in real-time and write them to the log file at the `DEBUG` level

### Requirement: Environment override isolation
The system SHALL only log the environment variables that are being explicitly overridden or added for a specific command execution.

#### Scenario: Logging environment
- **WHEN** a command is executed with `env={"PATH": "/foo"}`
- **THEN** the logs MUST show `PATH=/foo` but MUST NOT dump the entire host environment

### Requirement: Execution result tracking
The system SHALL log the exit code of every executed command and provide context on failure.

#### Scenario: Command failure
- **WHEN** a command exits with a non-zero status
- **THEN** the system MUST log the return code and raise an informative error containing the last few lines of output
