# Proposal: Smart Resolver

## Problem
The current resolver has a simpler search sequence and clones AUR repositories only at build time. This leads to issues where incorrect dependencies in an AUR package cannot be easily fixed because the PKGBUILD hasn't been cloned yet when the resolver tries to process its dependencies. Additionally, it lacks support for resolving virtual packages (via the `Provides` field) in official repositories.

## Proposed Change
Enhance the `DependencyResolver` with a more robust search sequence and early AUR cloning.

### Enhanced Search Sequence:
1. **Newly Created Packages**: Check `packages/` directory first.
2. **Official Repositories**:
   - First, search by package name.
   - Second, search the `Provides` field to resolve virtual dependencies (e.g., `python-yaml` providing `python-pyyaml`).
3. **AUR**:
   - First, check `aur_packages/` (local modifications or previous clones).
   - Second, query the AUR database. If found, **clone it immediately** to `aur_packages/`.
4. **PyPI**: Fallback to PyPI metadata and package generation.

## Impact
- **Fixability**: Users can modify AUR PKGBUILDs to fix dependency names before the build process starts.
- **Accuracy**: Virtual dependencies in official repos are correctly resolved.
- **Predictability**: The build order and dependency tree will be fully determined and fetched before any compilation begins.
