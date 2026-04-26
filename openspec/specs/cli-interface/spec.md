# Component: CLI Interface

## Purpose
The primary entry point for users to interact with the `aur-python-packer` tool. It handles argument parsing, configuration initialization, and orchestrates the build process via the `Manager`.

## Requirements

### Requirement: Configurable Work Directory
The CLI SHALL accept a `--work-dir` (or `-w`) option to specify the base directory for all tool state and artifacts.

#### Scenario: Custom work directory provided
- **WHEN** the user runs `aur-python-packer --work-dir /tmp/my-build build some-pkg`
- **THEN** the system uses `/tmp/my-build` as the root for state, cache, and repository

### Requirement: Directory-based State Isolation
All persistent data generated or used by the tool SHALL be stored within the specified `work_dir`.

#### Scenario: Internal path resolution
- **WHEN** a `work_dir` is set to `./work`
- **THEN** the state file SHALL be at `./work/state.json`
- **AND** the local repository SHALL be at `./work/repo/`
- **AND** the AUR cache SHALL be at `./work/aur_cache/`

### Requirement: Default Work Directory
If no `--work-dir` is provided, the CLI SHALL default to a directory named `work` within the project root.

#### Scenario: No work directory provided
- **WHEN** the user runs the tool without the `--work-dir` flag
- **THEN** the system defaults to using the `work/` directory in the current project root
