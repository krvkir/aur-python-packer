## MODIFIED Requirements

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
