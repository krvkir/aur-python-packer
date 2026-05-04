## ADDED Requirements

### Requirement: Cached Version Auditing
The system SHALL use the network response cache when fetching version metadata from PyPI during maintenance audits, serving cached data within TTL and falling back to stale data when network requests fail.

#### Scenario: Audit with cache hit
- **GIVEN** a fresh cached PyPI response for `python-foo` exists
- **WHEN** the auditor checks for updates to `python-foo`
- **THEN** the system SHALL compare the local version against the cached version metadata without a network request

#### Scenario: Audit with stale fallback
- **GIVEN** a stale cached PyPI response for `python-foo` exists
- **AND** the PyPI network request fails
- **WHEN** the auditor checks for updates to `python-foo`
- **THEN** the system SHALL compare the local version against the stale cached version metadata
- **AND** it SHALL log a warning about using stale data
