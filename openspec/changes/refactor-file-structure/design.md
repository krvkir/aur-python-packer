## Context

The current `aur_lifecycle_mgr` project is structured with a `manager/` subdirectory containing the source code, tests, and configuration. This fragmentation makes development and package management less intuitive. The tool uses a mix of build methods based on OS detection, which lacks consistency and security isolation. The state management is currently scattered across several default paths.

## Goals / Non-Goals

**Goals:**
- Unify the project structure at the repository root.
- Rename the package to `aur_python_packer` to better reflect its purpose.
- Centralize all tool-related state and artifacts within a configurable `work_dir`.
- Make chroot-based builds the default standard for security and isolation.
- Use Poetry for standardized dependency and environment management.

**Non-Goals:**
- Changing the core logic of dependency resolution or PyPI generation.
- Providing support for non-Arch-based distributions.

## Decisions

### Internal Architecture of `aur_python_packer`

The project will be restructured as a flat layout at the root. The `Manager` class will serve as the central hub, orchestrating interactions between specialized components.

- **`Manager`**: The top-level orchestrator. It receives a `work_dir` and `package_name` (if applicable) from the CLI.
- **`Builder` (formerly `BuildOrchestrator`)**: Handles the execution of build commands.
- **`StateManager`**: Manages the persistent build state (JSON).
- **`RepoManager`**: Manages the local pacman repository.
- **`DependencyResolver`**: Analyzes and determines build order.

### CLI and Manager Interaction

The CLI will be the primary entry point, handling argument parsing and passing configuration to the `Manager`.

1.  **Initialization**: CLI parses `--work-dir`, `--package-name`, and other flags.
2.  **Manager Setup**: CLI instantiates `Manager(work_dir=...)`.
3.  **Path Resolution**: The `Manager` resolves all internal paths (AUR cache, generated files, local repo, state file) relative to the provided `work_dir`.
4.  **Execution**: CLI calls `manager.build_all()` or other high-level methods.

### State Management in `work_dir`

To ensure portability and cleanliness, all stateful data will be contained within the `work_dir`.

- `work_dir/state.json`: Tracking build status of packages.
- `work_dir/repo/`: The local pacman repository.
- `work_dir/aur_cache/`: Cloned AUR repositories.
- `work_dir/generated/`: PKGBUILDs generated from PyPI.
- `work_dir/pacman.conf`: Custom configuration for chroot builds.

### Chroot-based Builder

The `Builder` will prioritize chroot builds to ensure a clean and isolated environment.

1.  **Check**: `Builder` checks for the existence of chroot tools (`extra-x86_64-build` on Arch, `buildpkg` on Manjaro).
2.  **Execution**: If tools are present, it executes the build in a chroot.
3.  **Strictness**: By default, the build will fail if chroot tools are missing.
4.  **Override**: A `--local` flag in the CLI will allow the `Manager` to instruct the `Builder` to use `makepkg` directly on the host system.

## Risks / Trade-offs

- **[Risk] Chroot requirements** → [Mitigation] Chroot builds require specific tools (`devtools` or `manjaro-tools-pkg`) and root privileges. The tool will verify tool presence and provide informative error messages.
- **[Risk] Breaking changes for existing installations** → [Mitigation] This refactor is considered a major version change. Documentation will specify the need to transition to the new structure and `work_dir` approach.
- **[Risk] Sudo usage in automation** → [Mitigation] Chroot tools usually require sudo. Users must ensure NOPASSWD is configured for these specific tools or run the tool in an environment where sudo is available.
