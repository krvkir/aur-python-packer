## Why

The current version of the tool has several usability and organizational issues:
- Diagnostic logs are cluttered with verbose Bubblewrap arguments, making them hard to read.
- Large dependency graphs overwhelm the terminal output.
- Certain logs are redundant (duplicate messages).
- The "home" directory is misplaced in the workspace root instead of the internal state directory.
- Dependency tier identification becomes inaccurate once an AUR package is cloned locally.
- Git integration for package maintenance is less efficient and doesn't respect host identity.

## What Changes

- **Improved Sandbox Logging**: `bwrap` arguments are now hidden at INFO level, replaced by a summary of the environment.
- **Smart Graph Visualization**: Repositories dependencies are hidden for graphs with >20 nodes unless `--show-repo-deps` is used.
- **Log De-duplication**: Fixed redundant "Starting sandboxed build" messages.
- **Accurate Tier Tracking**: AUR packages retain their "aur" tier even after being cloned locally.
- **Streaming Git Operations**: `git-show` now prints results incrementally.
- **Host Git Identity**: `git-init` uses the host's global Git configuration for user name and email.
- **Workspace Reorganization**: The sandboxed `home/` directory is moved to `srv/home/`.

## Capabilities

### New Capabilities
- (none)

### Modified Capabilities
- `system-diagnostics`: Update command invocation tracking to support concise INFO-level summaries of sandboxed environments and prevent duplicate logging.
- `user-interaction-interface`: Update workspace structure (relocate home), graph visualization (omit repo deps for large graphs), and Git integration (streaming output, host identity).
- `dependency-resolution`: Refine tier identification logic to distinguish between "local" (user-created) and "aur" (locally cloned AUR) packages correctly.

## Impact

- `aur_python_packer/sandbox.py`: Changes to bwrap command construction and logging.
- `aur_python_packer/utils.py`: `run_command` signature change to support summaries.
- `aur_python_packer/graph_utils.py`: Logic for filtering nodes and handling the new visualization flag.
- `aur_python_packer/resolver.py`: Adjustments to tier classification in `resolve()`.
- `aur_python_packer/main.py`: Update git initialization logic, streaming diffs, and workspace paths.
- `aur_python_packer/cli.py`: New flag for the `build` and `resolve` commands.
