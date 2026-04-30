# Proposal: New CLI Commands and Options

## Problem
Currently, it is difficult to track manual changes to generated or cloned PKGBUILDs. Additionally, users sometimes need to force-add a dependency to a package without modifying its PKGBUILD file directly (e.g., for testing or fixing broken metadata on the fly).

## Proposed Change
Add new maintenance commands and a flexible dependency injection option.

### New Commands:
1. **`git-init`**: Automatically initializes Git repositories in all local package directories (`packages/` and `aur_packages/`). This provides a baseline for tracking changes. It uses the `git` tool available within the chroot environment.
2. **`git-show`**: Lists all package directories where the `PKGBUILD` has changed relative to its last committed state. This helps users quickly identify their manual modifications.

### New Build Option:
- **`-d` / `--depends`**: Allows specifying additional dependencies for a build.
  - It is repeatable: `-d pkg1 -d pkg2`.
  - Injected dependencies are added to the dependency graph and resolved normally (searching Local -> Repo -> AUR -> PyPI).
  - Successful builds with injected dependencies are recorded in the build index.

## Impact
- **Version Control**: Built-in git integration makes it easy to track and revert manual changes to PKGBUILDs.
- **Flexibility**: The `-d` option allows for rapid experimentation and "hot-fixing" dependencies without dirtying the source metadata.
- **Transparency**: All modifications (manual or via injection) are visible and trackable.
