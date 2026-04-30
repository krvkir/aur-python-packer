# Capability: System Diagnostics (Refinement)

## Requirements

### Requirement: Automatic Log Management (Updated)
The system SHALL ensure the diagnostic logs are stored within a dedicated `logs/` directory inside the configured workspace.

#### Scenario: Log directory initialization
- **GIVEN** the application starts
- **WHEN** the workspace is initialized
- **THEN** the system MUST ensure a `logs/` directory exists within it for storing session logs.
