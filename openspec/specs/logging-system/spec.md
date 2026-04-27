# Component: Logging System

## Purpose
Provides the infrastructure for dual-output logging, ensuring that both high-level terminal progress and detailed file-based diagnostics are captured consistently across the application's lifecycle.

## Requirements

### Requirement: Dual-output logging
The system SHALL support concurrent logging to both the terminal and a persistent log file.

#### Scenario: Normal execution
- **WHEN** the application is running
- **THEN** high-level progress (INFO+) MUST appear on the terminal
- **THEN** detailed diagnostics (DEBUG+) MUST be written to the log file

### Requirement: Automatic log directory management
The system SHALL ensure the `logs/` directory exists within the current working directory before starting any logging.

#### Scenario: Missing logs directory
- **WHEN** the application starts and the `logs/` directory does not exist
- **THEN** the system MUST create the `logs/` directory automatically

### Requirement: Timestamped log filenames
The system SHALL generate unique, timestamped filenames for each execution's log file.

#### Scenario: Log file creation
- **WHEN** a new session begins
- **THEN** a log file with the format `run_YYYYMMDD_HHMMSS.log` MUST be created in the `logs/` directory

### Requirement: Standardized log format
The system SHALL use a consistent log format including timestamp, log level, logger name, and message.

#### Scenario: Log entry inspection
- **WHEN** reviewing the log file
- **THEN** each entry MUST contain `YYYY-MM-DD HH:MM:SS [LEVEL] NAME: MESSAGE`
