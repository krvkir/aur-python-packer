## 1. Directory Structure and Package Setup

- [ ] 1.1 Create `src/` and `tests/` directories at the repository root.
- [ ] 1.2 Move `manager/src/aur_lifecycle_mgr` to `src/aur_python_packer`.
- [ ] 1.3 Move contents of `manager/tests/` to `tests/`.
- [ ] 1.4 Delete the `manager/` directory.
- [ ] 1.5 Initialize Poetry configuration in `pyproject.toml` at the root, setting the name to `aur_python_packer`.
- [ ] 1.6 Migrate dependencies (`click`, `networkx`, `jinja2`, `requests`) and dev-dependencies (`pytest`) to `pyproject.toml`.
- [ ] 1.7 Update `Makefile` at the root to use `poetry run` for tests and fix paths.

## 2. Path Resolution & State Management

- [ ] 2.1 Update `aur_python_packer/main.py` (Manager class) to accept `work_dir` in `__init__`.
- [ ] 2.2 Refactor `Manager` to calculate `state_path`, `repo_path`, `aur_cache_path`, and `generated_path` as subdirectories of `work_dir`.
- [ ] 2.3 Update `StateManager` (`aur_python_packer/state.py`) to accept and use the explicit state file path.
- [ ] 2.4 Update `RepoManager` (`aur_python_packer/repo.py`) to accept and use the explicit repository path.

## 3. Builder Refactoring & Chroot Support

- [ ] 3.1 Rename `BuildOrchestrator` to `Builder` in `aur_python_packer/builder.py` and update all references.
- [ ] 3.2 Implement `Builder.check_chroot_tools()` to detect `extra-x86_64-build` (Arch) or `buildpkg` (Manjaro).
- [ ] 3.3 Implement `Builder.execute_chroot_build()` to run the appropriate chroot build command.
- [ ] 3.4 Implement `Builder.execute_local_build()` to run `makepkg`.
- [ ] 3.5 Update `Builder.build()` to prioritize chroot builds, falling back to local only if the `--local` flag is set.

## 4. CLI Interface & Integration

- [ ] 4.1 Update `aur_python_packer/cli.py` to add the `--work-dir` / `-w` option (defaulting to `work`).
- [ ] 4.2 Update `aur_python_packer/cli.py` to add the `--local` boolean flag.
- [ ] 4.3 Update the CLI entry point to pass these new parameters when instantiating the `Manager`.
- [ ] 4.4 Global find-and-replace for all imports: rename `aur_lifecycle_mgr` to `aur_python_packer`.

## 5. Verification

- [ ] 5.1 Update test suite to use the new package name and directory structure.
- [ ] 5.2 Add a new test case in `tests/test_manager.py` to verify all state files are created within the specified `work_dir`.
- [ ] 5.3 Add test cases for `Builder` to verify it correctly identifies system build tools.
- [ ] 5.4 Run the full test suite with `poetry run pytest` and ensure all tests pass.
