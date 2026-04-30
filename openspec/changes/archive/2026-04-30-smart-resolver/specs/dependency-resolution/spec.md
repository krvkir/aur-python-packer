# Capability: Dependency Resolution (Refinement)

## MODIFIED Requirements

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

## ADDED Requirements

### Requirement: Early AUR Acquisition
The system SHALL clone the AUR repository for a dependency immediately upon identifying it in the AUR database, ensuring the PKGBUILD is available for inspection before further resolution.

#### Scenario: Immediate clone
- **GIVEN** a dependency is found in the AUR RPC
- **WHEN** the resolver identifies the package
- **THEN** the system SHALL clone the repository into `aur_packages/`
- **AND** it SHALL then use the local files in `aur_packages/` to continue dependency resolution.
