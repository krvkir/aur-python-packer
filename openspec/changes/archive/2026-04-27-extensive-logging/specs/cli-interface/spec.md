## ADDED Requirements

### Requirement: Log file path visibility
The CLI SHALL print the absolute path to the current session's log file to the terminal at the beginning of the run.

#### Scenario: User feedback on startup
- **WHEN** the tool starts
- **THEN** it MUST print a message like "Logging to: /path/to/work/logs/run_timestamp.log" before performing any other actions
