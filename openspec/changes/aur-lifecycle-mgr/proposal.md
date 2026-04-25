## Why

The current process for maintaining and testing AUR packages for JupyterAI and its dependencies is manual, error-prone, and inconsistent. A robust, automated system is needed to resolve recursive dependencies, build in clean environments (chroot), and keep packages synchronized with upstream PyPI versions to ensure a reliable installation experience for Arch Linux and Manjaro users.

## What Changes

- Automated recursive dependency resolution across local directories, official repositories, AUR, and PyPI.
- Hermetic build system using clean chroots (distro-aware for Arch and Manjaro).
- Dynamic PKGBUILD generation for missing Python dependencies using PyPI metadata.
- Automated version auditing and update cycle for local package sets.
- Local repository management to facilitate dependency injection into build environments.
- State tracking and resume capability for complex multi-package build sequences.

## Capabilities

### New Capabilities
- `dependency-resolver`: Logic to build a dependency graph by querying multiple tiers (Local, Repo, AUR, PyPI) and performing topological sorts.
- `package-generator`: Tooling to create functional PKGBUILDs from PyPI metadata for missing python dependencies.
- `chroot-builder`: Distro-aware orchestration of clean chroot builds (using devtools or Manjaro's buildpkg).
- `repo-manager`: Management of a local pacman repository and automated configuration of build chroots to use it.
- `maintenance-manager`: Version auditing against PyPI and automated update triggering for the local package set.

### Modified Capabilities
- None

## Impact

- **Build Infrastructure**: Requires `devtools` (Arch) or `manjaro-tools` (Manjaro).
- **Storage**: Requires local storage for the package repository and chroot environments.
- **Dependencies**: Depends on `python-pip`, `pacman`, and potentially `pip2pkgbuild` or similar logic.
- **AUR/PyPI APIs**: Relies on network access to AUR (RPC) and PyPI (JSON API).
