# Capability: Dependency Resolution

## Purpose
Calculates the full dependency tree for a target package and determines the optimal build order while ensuring no circular dependencies exist.
## Requirements
### Requirement: Multi-Tier Resolution
The system SHALL resolve dependencies using a prioritized search sequence that accounts for local modifications and virtual package provisions.

#### Search Sequence Order:
1. **Newly Created Packages**: Search the `packages/` directory within the workspace.
2. **Official Repositories**:
   - First, search by package name.
   - Second, search the "Provides" field of all repository packages.
3. **AUR**:
   - First, search the `aur_packages/` directory for local AUR clones.
   - Second, search the AUR database via RPC.
4. **PyPI**: Fallback to querying PyPI if not found in preceding tiers.

#### Scenario: Resolve via Provides field
- **GIVEN** a package depends on `python-pyyaml`
- **AND** `python-pyyaml` is not a package name but is provided by `python-yaml` in official repos
- **WHEN** resolving the dependency
- **THEN** the system SHALL resolve the dependency to `python-yaml`.

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

### Requirement: Early AUR Acquisition
The system SHALL clone the AUR repository for a dependency immediately upon identifying it in the AUR database, ensuring the PKGBUILD is available for inspection before further resolution.

#### Scenario: Immediate clone
- **GIVEN** a dependency is found in the AUR RPC
- **WHEN** the resolver identifies the package
- **THEN** the system SHALL clone the repository into `aur_packages/`
- **AND** it SHALL then use the local files in `aur_packages/` to continue dependency resolution.

## Implementation Notes
- Searches Local, Official Repos, AUR, and PyPI.
- Verifies exact name existence on PyPI.
- Uses a topological sort algorithm for build ordering.
