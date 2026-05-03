# Capability: Dependency Resolution

## Purpose
Calculates the full dependency tree for a target package and determines the optimal build order while ensuring no circular dependencies exist.
## Requirements
### Requirement: Multi-Tier Resolution
The system SHALL resolve dependencies using a prioritized search sequence that accounts for local modifications and virtual package provisions. The tier assigned to a package SHALL reflect its origin directory.

#### Search Sequence Order:
1. **Newly Created Packages**: Search the `packages/` directory within the workspace. Packages found here MUST be assigned the **local** tier.
2. **Official Repositories**:
   - First, search by package name.
   - Second, search the "Provides" field of all repository packages.
   Packages found here MUST be assigned the **repo** tier.
3. **AUR**:
   - First, search the `aur_packages/` directory for local AUR clones. Packages found here MUST be assigned the **aur** tier.
   - Second, search the AUR database via RPC. Packages found here MUST be assigned the **aur** tier.
4. **PyPI**: Fallback to querying PyPI if not found in preceding tiers. Packages found here MUST be assigned the **pypi** tier.

#### Scenario: AUR package tier persistence
- **GIVEN** an AUR package `aur-pkg` has been cloned to `aur_packages/aur-pkg`
- **WHEN** the system resolves dependencies
- **THEN** `aur-pkg` MUST be identified as tier **aur**
- **AND** it MUST NOT be identified as tier **local** even if `aur_packages/` is checked during search.

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


### Requirement: Ad-hoc Dependency Injection
The system SHALL support the injection of arbitrary dependencies into the build graph of a target package.

#### Scenario: Injecting multiple dependencies
- **GIVEN** a build request for `pkg-a`
- **WHEN** the user provides `-d pkg-b -d pkg-c`
- **THEN** the resolver SHALL treat `pkg-b` and `pkg-c` as direct dependencies of `pkg-a`.
- **AND** it SHALL resolve `pkg-b` and `pkg-c` using the standard multi-tier search process.
## Implementation Notes
- Searches Local, Official Repos, AUR, and PyPI.
- Verifies exact name existence on PyPI.
- Uses a topological sort algorithm for build ordering.
