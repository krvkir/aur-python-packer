## 1. Project Infrastructure

- [ ] 1.1 Set up Python project structure (src, tests, templates).
- [ ] 1.2 Implement basic CLI interface using `click` or `argparse`.
- [ ] 1.3 Initialize state management (`build_state.json` schema).

## 2. Dependency Resolution

- [ ] 2.0 Prepare unit and integration tests for dependency resolution tiers and graph logic.
- [ ] 2.1 Implement metadata parser for local `PKGBUILD` and `.SRCINFO` files.
- [ ] 2.2 Add official repository lookup using `pacman -Si`.
- [ ] 2.3 Implement AUR RPC client to fetch dependency info.
- [ ] 2.4 Build dependency graph logic using `networkx`.
- [ ] 2.5 Implement topological sort and circular dependency detection.
- [ ] 2.6 Verify all dependency resolution tests pass.

## 3. PKGBUILD Generator (PyPI)

- [ ] 3.0 Prepare unit tests for PyPI API client and PKGBUILD templating.
- [ ] 3.1 Implement PyPI JSON API client.
- [ ] 3.2 Create Jinja2 template for Python `PKGBUILD` generation.
- [ ] 3.3 Implement source fetching and automated SHA256 checksum calculation.
- [ ] 3.4 Implement `.SRCINFO` generation using `makepkg --printsrcinfo`.
- [ ] 3.5 Verify all generator tests pass.

## 4. Local Repository Management

- [ ] 4.0 Prepare tests for repo management and config injection (using mocks/temp dirs).
- [ ] 4.1 Implement local directory manager for built packages.
- [ ] 4.2 Add `repo-add` wrapper for maintaining the package database.
- [ ] 4.3 Create utility to modify chroot `pacman.conf` with local repo settings.
- [ ] 4.4 Verify all repo management tests pass.

## 5. Build Orchestration

- [ ] 5.0 Prepare tests for OS detection and build tool wrappers (using mocks).
- [ ] 5.1 Implement host OS detection (Arch vs Manjaro).
- [ ] 5.2 Add wrapper for `extra-x86_64-build` (Arch).
- [ ] 5.3 Add wrapper for `buildpkg` (Manjaro).
- [ ] 5.4 Implement build success verification and package moving logic.
- [ ] 5.5 Verify all build orchestration tests pass.

## 6. Maintenance & Auditing

- [ ] 6.0 Prepare tests for version auditing logic.
- [ ] 6.1 Implement version auditing logic comparing local state to PyPI.
- [ ] 6.2 Add command to trigger automated package updates (bump version, re-checksum).
- [ ] 6.3 Verify all auditing tests pass.

## 7. Integration & Final Verification

- [ ] 7.0 Prepare end-to-end integration tests for the full "build-all" lifecycle.
- [ ] 7.1 Integrate all components into a main "build-all" command.
- [ ] 7.2 Implement "resume" capability from `build_state.json`.
- [ ] 7.3 Execute end-to-end tests on a small subset of JupyterAI dependencies.
- [ ] 7.4 Verify all system integration tests pass.
