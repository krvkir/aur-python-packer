## ADDED Requirements

### Requirement: Cached External Lookups
The system SHALL use the network response cache when querying AUR and PyPI during dependency resolution, serving cached data within TTL and falling back to stale data when network requests fail.

#### Scenario: AUR resolution with cache hit
- **GIVEN** a fresh cached AUR response for `example-pkg` exists
- **WHEN** the resolver queries AUR for `example-pkg`
- **THEN** the system SHALL return the cached result without contacting the AUR RPC

#### Scenario: PyPI resolution with stale fallback
- **GIVEN** a stale cached PyPI response for `python-example` exists
- **AND** the PyPI network request fails
- **WHEN** the resolver queries PyPI for `python-example`
- **THEN** the system SHALL return the stale cached metadata
- **AND** it SHALL log a warning about using stale data
