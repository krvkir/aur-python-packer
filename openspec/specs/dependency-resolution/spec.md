# Capability: Dependency Resolution

## Purpose
Calculates the full dependency tree for a target package and determines the optimal build order while ensuring no circular dependencies exist.

## Requirements

### Requirement: Multi-Tier Resolution
The system SHALL resolve dependencies by searching through multiple sources in a defined priority order:
1. **Local Repository**: Packages already built and present in the local database.
2. **Official Repositories**: Packages available via `pacman` (Core, Extra, etc.).
3. **AUR**: Arch User Repository for community-maintained PKGBUILDs.
4. **PyPI**: Python Package Index for packages not yet in Arch-compatible format.

#### Scenario: Resolve from Local Repository
- **GIVEN** a dependency exists in the local repository
- **WHEN** searching for the package
- **THEN** the system SHALL mark it as already available locally

#### Scenario: Resolve from Official Repositories
- **GIVEN** a dependency exists in the official Arch repositories (e.g., `python-requests`)
- **WHEN** searching for the package
- **THEN** the system SHALL mark it as a system dependency to be installed via `pacman`

#### Scenario: Resolve from AUR
- **GIVEN** a dependency exists in the AUR (e.g., `python-some-aur-pkg`)
- **WHEN** searching for the package
- **THEN** the system SHALL fetch the PKGBUILD from AUR and add it to the build queue

#### Scenario: Resolve from PyPI
- **GIVEN** a dependency exists only on PyPI (e.g., `new-python-lib`)
- **WHEN** searching for the package
- **THEN** the system SHALL initiate the package generation process for an Arch-compatible PKGBUILD

### Requirement: Build Order Calculation
The system SHALL determine a build sequence that ensures all dependencies are built before the packages that require them.

#### Scenario: Topological sorting
- **GIVEN** a set of packages with interdependencies
- **WHEN** calculating the build order
- **THEN** the system SHALL produce a sequence where every package follows its dependencies

### Requirement: Circular Dependency Detection
The system SHALL detect and report any cycles in the dependency graph to prevent infinite loops.

#### Scenario: Cycle detection
- **GIVEN** a circular dependency exists between packages
- **WHEN** analyzing the graph
- **THEN** the system SHALL raise an error and abort the process

## Implementation Notes
- Searches Local, Official Repos, AUR, and PyPI.
- Verifies exact name existence on PyPI.
- Uses a topological sort algorithm for build ordering.
