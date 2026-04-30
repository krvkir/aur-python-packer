# Capability: Dependency Resolution (Refinement)

## Requirements

### Requirement: Ad-hoc Dependency Injection
The system SHALL support the injection of arbitrary dependencies into the build graph of a target package.

#### Scenario: Injecting multiple dependencies
- **GIVEN** a build request for `pkg-a`
- **WHEN** the user provides `-d pkg-b -d pkg-c`
- **THEN** the resolver SHALL treat `pkg-b` and `pkg-c` as direct dependencies of `pkg-a`.
- **AND** it SHALL resolve `pkg-b` and `pkg-c` using the standard multi-tier search process.
