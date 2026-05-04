# Capability: Network Response Caching

## Purpose
Manages the lifecycle, storage, and retrieval of external API responses with TTL enforcement and stale-data fallback for offline resilience.

## Requirements

### Requirement: Client-Specific Cache Storage
The system SHALL store cached network responses in client-specific subdirectories under `<workdir>/srv/network_cache/`.

#### Scenario: Cache directory layout
- **GIVEN** a workspace at `./work`
- **WHEN** the caching system initializes
- **THEN** cache files for AUR requests MUST reside in `work/srv/network_cache/aur/`
- **AND** cache files for PyPI requests MUST reside in `work/srv/network_cache/pypi/`

#### Scenario: Cache directories are persistent
- **GIVEN** cache directories exist
- **WHEN** the tool runs multiple sessions
- **THEN** the system SHALL NOT delete or wipe cache directory contents between sessions

### Requirement: Metadata-Only Caching
The system SHALL cache only API metadata responses (JSON). The system SHALL NOT cache large binary artifacts such as source tarballs.

#### Scenario: Cached response content
- **GIVEN** a PyPI metadata request to `https://pypi.org/pypi/requests/json`
- **WHEN** the response is cached
- **THEN** the cache file MUST contain the JSON metadata (name, version, requires_dist, etc.)
- **AND** the cache file MUST NOT contain the source tarball content

### Requirement: TTL-Based Staleness
The system SHALL treat cached responses older than 1 hour as stale.

#### Scenario: Fresh cache hit
- **GIVEN** a cached PyPI response for `python-foo` stored 30 minutes ago
- **WHEN** the system requests metadata for `python-foo`
- **THEN** the system SHALL serve the cached response without a network request

#### Scenario: Stale cache with successful refresh
- **GIVEN** a cached AUR response for `foo-git` stored 90 minutes ago
- **WHEN** the system requests info for `foo-git`
- **THEN** the system SHALL attempt a network refresh
- **AND** if the network request succeeds, it SHALL update the cache and return the fresh data

### Requirement: Stale Fallback on Network Failure
The system SHALL return stale cached data when a network refresh attempt fails, logging an appropriate warning.

#### Scenario: Offline fallback
- **GIVEN** a cached AUR response for `foo-git` stored 90 minutes ago
- **AND** the network is unavailable
- **WHEN** the system requests info for `foo-git`
- **THEN** the system SHALL log a warning that stale data is being used
- **AND** it SHALL return the stale cached data

#### Scenario: No cache and no network
- **GIVEN** no cached response exists for `python-bar`
- **AND** the network is unavailable
- **WHEN** the system requests metadata for `python-bar`
- **THEN** the system SHALL raise an error indicating the request failed

### Requirement: Negative Result Caching
The system SHALL cache non-existent (404) lookup results to avoid repeated failed network requests.

#### Scenario: Cached 404
- **GIVEN** a PyPI request for `python-nonexistent` returns 404
- **WHEN** the system caches the result
- **THEN** subsequent requests for `python-nonexistent` SHALL return a cached "not found" result if within TTL

## Implementation Notes
- Cache files are stored as JSON with `url`, `timestamp`, and `data` fields.
- A cached 404 is represented as `data: null` in the cache file.
- Directory creation uses `os.makedirs` for the client-specific subdirectories.
