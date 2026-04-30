# Proposal: File System Cleanup

## Problem
The current workspace directory structure is somewhat flat and mixes user-accessible package directories with internal tool state (like `pacman_db`, `gnupg`, etc.). This makes it harder to manage and less intuitive for users who might want to interact with the built packages or logs.

## Proposed Change
Reorganize the workspace directory (`work_dir`) into a structured layout that clearly separates:
1. **Package Sources**: `aur_packages/` (from AUR) and `packages/` (from PyPI).
2. **Built Artifacts**: `local_repo/` (the actual pacman repository).
3. **Diagnostics**: `logs/`.
4. **Internal State**: `srv/` (everything the tool needs to function but the user shouldn't touch).
5. **Configuration**: `pypi_mapping.json` at the root for easy access.

## New Structure
```text
work_dir/
├── aur_packages/       # AUR package clones
├── packages/           # Generated PyPI packages
├── local_repo/         # Built packages and repo DB
├── logs/               # Log files
├── srv/                # Internal tool state
│   ├── build_index.json
│   ├── pacman_db/      # Sync DBs
│   ├── pacman_cache/   # Package cache
│   ├── pacman.log      # Pacman operation log
│   ├── gnupg/          # GPG keys for signing (if used)
│   └── root/           # Chroot root filesystem (sandbox)
└── pypi_mapping.json   # Package name mapping
```

## Impact
- **Cleanliness**: Users have a clear view of their packages and logs.
- **Isolation**: Internal tool state is tucked away in `srv/`.
- **Maintainability**: Paths are centralized and easier to manage in the code.
