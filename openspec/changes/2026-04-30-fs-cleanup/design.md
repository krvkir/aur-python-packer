# Design: File System Cleanup

## Architectural Overview
The `Manager` class will be the primary point of change, as it initializes and manages these paths. The `Builder`, `RepoManager`, and `DependencyResolver` will need to be updated to use the new path structure provided by the `Manager`.

## Component Changes

### 1. `Manager` (`aur_python_packer/main.py`)
- Update `__init__` to define the new paths.
- Ensure all directories are created upon initialization.
- Move `build_index.json` to `srv/`.

### 2. `RepoManager` (`aur_python_packer/repo.py`)
- Update to look for built packages and the database in `local_repo/`.
- Ensure internal pacman paths (db, cache, log) are correctly routed to `srv/`.

### 3. `DependencyResolver` (`aur_python_packer/resolver.py`)
- Update `_load_mapping` to look for `pypi_mapping.json` in the workspace root.
- Update search paths to include `packages/` and `aur_packages/`.

### 4. `Builder` and `Sandbox` (`aur_python_packer/builder.py`, `aur_python_packer/sandbox.py`)
- Update the root directory path to `srv/root/`.

### 5. `Logger` (`aur_python_packer/logger.py`)
- Update to store logs in `logs/` directory.

## Migration Path
Since the workspace is essentially a cache and build area, a clean break is acceptable. Users can either delete their old `work/` directory or the tool will simply start fresh in the new structure. No complex data migration is required.
