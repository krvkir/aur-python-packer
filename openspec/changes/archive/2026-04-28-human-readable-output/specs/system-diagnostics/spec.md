## MODIFIED Requirements

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
