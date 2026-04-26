# pypi-lookup Specification

## Purpose
TBD - created by archiving change pypi-lookup. Update Purpose after archive.
## Requirements
### Requirement: Exact Package Verification
The system SHALL verify the existence of a package on PyPI using the exact name via the JSON API.

#### Scenario: Package exists on PyPI
- **WHEN** the system queries `https://pypi.org/pypi/fastmcp/json`
- **THEN** it SHALL receive a 200 OK response and confirm package existence.

#### Scenario: Package does not exist on PyPI
- **WHEN** the system queries `https://pypi.org/pypi/non-existent-pkg-xyz/json`
- **THEN** it SHALL receive a 404 response and mark the package as not found on PyPI.

### Requirement: Metadata Extraction
The system SHALL extract the package version, license, and dependencies from the PyPI JSON response.

#### Scenario: Extract dependencies
- **WHEN** the system fetches metadata for `fastmcp`
- **THEN** it SHALL extract the `requires_dist` list from the `info` object.

