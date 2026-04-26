# Component: Dependency Resolver

## Purpose
Responsible for building and analyzing the dependency graph for a target package. It performs multi-tier lookups (Local, Official Repos, AUR, PyPI) to resolve every dependency and calculates the optimal build order using topological sorting. It also detects circular dependencies to prevent build-loop deadlocks.

## Requirements

### Requirement: Multi-tier Dependency Resolution
The system SHALL resolve dependencies by searching through the following tiers in order:
1. Local directories containing a `PKGBUILD`.
2. Official Arch/Manjaro repositories.
3. The Arch User Repository (AUR).
4. The Python Package Index (PyPI) for `python-*` packages.

#### Scenario: Resolve local package
- **WHEN** a dependency exists as a folder with a PKGBUILD in the search path
- **THEN** the system SHALL mark it as a "Local" dependency and parse its metadata.

#### Scenario: Resolve AUR package
- **WHEN** a dependency is not found locally or in official repos but exists in AUR
- **THEN** the system SHALL fetch its source/SRCINFO from AUR.

### Requirement: Topological Sort
The system SHALL produce a build order such that dependencies are built before the packages that require them.

#### Scenario: Basic linear dependency
- **WHEN** Package A depends on Package B
- **THEN** the system SHALL order the build as B, then A.

#### Scenario: Detect circular dependencies
- **WHEN** Package A depends on B, and B depends on A
- **THEN** the system SHALL raise a clear error identifying the cycle and abort.
