## 1. Project Infrastructure

- [x] 1.1 Set up Python project structure (src, tests, templates).
- [x] 1.2 Implement basic CLI interface using `click` or `argparse`.
- [x] 1.3 Initialize state management (`build_state.json` schema).

## 2. Dependency Resolution

- [x] 2.0 Prepare unit and integration tests for dependency resolution tiers and graph logic.
- [x] 2.1 Implement metadata parser for local `PKGBUILD` and `.SRCINFO` files.
- [x] 2.2 Add official repository lookup using `pacman -Si`.
- [x] 2.3 Implement AUR RPC client to fetch dependency info.
- [x] 2.4 Build dependency graph logic using `networkx`.
- [x] 2.5 Implement topological sort and circular dependency detection.
- [x] 2.6 Verify all dependency resolution tests pass.

## 3. PKGBUILD Generator (PyPI)

- [x] 3.0 Prepare unit tests for PyPI API client and PKGBUILD templating.
- [x] 3.1 Implement PyPI JSON API client.
- [x] 3.2 Create Jinja2 template for Python `PKGBUILD` generation.
- [x] 3.3 Implement source fetching and automated SHA256 checksum calculation.
- [x] 3.4 Implement `.SRCINFO` generation using `makepkg --printsrcinfo`.
- [x] 3.5 Verify all generator tests pass.

## 4. Local Repository Management

- [x] 4.0 Prepare tests for repo management and config injection (using mocks/temp dirs).
- [x] 4.1 Implement local directory manager for built packages.
- [x] 4.2 Add `repo-add` wrapper for maintaining the package database.
- [x] 4.3 Create utility to modify chroot `pacman.conf` with local repo settings.
- [x] 4.4 Verify all repo management tests pass.

## 5. Build Orchestration

- [x] 5.0 Prepare tests for OS detection and build tool wrappers (using mocks).
- [x] 5.1 Implement host OS detection (Arch vs Manjaro).
- [x] 5.2 Add wrapper for `extra-x86_64-build` (Arch).
- [x] 5.3 Add wrapper for `buildpkg` (Manjaro).
- [x] 5.4 Implement build success verification and package moving logic.
- [x] 5.5 Verify all build orchestration tests pass.

## 6. Maintenance & Auditing

- [x] 6.0 Prepare tests for version auditing logic.
- [x] 6.1 Implement version auditing logic comparing local state to PyPI.
- [x] 6.2 Add command to trigger automated package updates (bump version, re-checksum).
- [x] 6.3 Verify all auditing tests pass.

## 7. Integration & Final Verification

- [x] 7.0 Prepare end-to-end integration tests for the full "build-all" lifecycle.
- [x] 7.1 Integrate all components into a main "build-all" command.
- [x] 7.2 Implement "resume" capability from `build_state.json`.
- [x] 7.3 Execute end-to-end tests on a small subset of JupyterAI dependencies.
- [x] 7.4 Verify all system integration tests pass.
