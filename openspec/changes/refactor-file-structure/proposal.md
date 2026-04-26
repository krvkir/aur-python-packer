## Why

The current project structure is fragmented and the package naming does not accurately reflect its purpose. This change centralizes the codebase into a unified repository structure and renames the package to `aur-python-packer` to improve maintainability and clarity.

## What Changes

- **Project Consolidation**: Move `.git`, `pyproject.toml`, `Makefile`, and `tests/` from the subdirectory to the root `~/repos/archlinux/aur-python-packer`.
- **Package Renaming**: Rename the core Python package from `aur_lifecycle_mgr` to `aur_python_packer`.
- **Environment Management**: Switch to Poetry for dependency and environment management.
- **CLI Enhancement**: Update the CLI to accept `work_dir` and `package_name` parameters.
- **Builder Standardization**: Implement chroot-based builds by default, failing if chroot is missing unless the `--local` flag is provided.
- **Work Directory**: Ensure the tool's internal "work" directory is located inside the project folder.

## Capabilities

### New Capabilities
- `cli-interface`: Command-line interface for managing AUR Python packages with specific parameters and build flags.
- `chroot-builder`: Secure and isolated build environment using chroot by default.
- `project-structure`: Standardized layout and Poetry-based environment for the `aur-python-packer` project.

### Modified Capabilities
*None*

## Impact

- **Codebase**: Major file movements and package renaming will affect all source files and imports.
- **Development Workflow**: Developers will need to use Poetry for managing dependencies and environments.
- **Build Process**: The default build method shifts to chroot, requiring appropriate system permissions and setup.
- **Configuration**: Existing scripts or CI/CD pipelines will need updates to reflect the new paths and package names.
