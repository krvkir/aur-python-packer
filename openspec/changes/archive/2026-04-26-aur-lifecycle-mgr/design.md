## Context

The project aims to manage a large set of interconnected AUR packages for JupyterAI. The current state is a collection of `PKGBUILD` files that are manually managed and often outdated. Dependency resolution is difficult because many dependencies are themselves in the AUR and not yet built.

## Goals / Non-Goals

**Goals:**
- Provide a single command to build a target package and all its missing dependencies in the correct order.
- Ensure all builds happen in a clean, isolated environment (chroot).
- Automatically generate PKGBUILDs for Python dependencies not found in the AUR or local set.
- Maintain a local pacman repository to serve as a cache and dependency source for the chroot.

**Non-Goals:**
- Replacing existing AUR helpers for general use.
- Automated uploading to the AUR (this remains a manual verification step).
- Support for non-Arch-based distributions.

## Decisions

- **Orchestration Language**: Python. Rationale: Superior handling of dependency graphs, JSON/PyPI APIs, and process orchestration compared to Bash.
- **Dependency Resolution**:
    - Build an in-memory graph using `networkx` or similar logic.
    - Check tiers: Local FS -> Official Repos (`pacman -Si`) -> AUR (RPC) -> PyPI.
- **Build Isolation**: 
    - Use `extra-x86_64-build` (Arch) and `buildpkg` (Manjaro).
    - Rational: These are the standard tools for clean chroot builds on their respective platforms.
- **Local Repository**:
    - Maintain a flat directory of `.pkg.tar.zst` files.
    - Use `repo-add` to generate the database.
    - Inject this repo into the chroot's `/etc/pacman.conf`.
- **PKGBUILD Generation**:
    - Use a Jinja2 template for Python packages.
    - Fetch version and dependency info from PyPI JSON API.
- **State Management**:
    - Use a JSON file (`build_state.json`) to track package versions, build timestamps, and success/failure status.

## Risks / Trade-offs

- **[Risk]** Circular dependencies in Python packages. → **Mitigation**: Detect cycles in the graph and abort with a clear error, requiring manual "bootstrap" PKGBUILDs.
- **[Risk]** Host/Chroot mismatch (Arch vs Manjaro). → **Mitigation**: Auto-detect host OS and use the appropriate tooling and mirrorlists.
- **[Risk]** API rate limiting (AUR/PyPI). → **Mitigation**: Implement local caching of metadata.
