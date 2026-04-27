## 1. Core Logging Infrastructure

- [ ] 1.1 Create `aur_python_packer/logger.py` with `setup_logging(work_dir)` function.
- [ ] 1.2 Implement dual handlers (Terminal: INFO, File: DEBUG) and standardized formatting.
- [ ] 1.3 Ensure `logs/` directory creation within the provided `work_dir`.
- [ ] 1.4 Update `aur_python_packer/cli.py` to initialize logging and print the log path on startup.

## 2. Command Execution Wrapper

- [ ] 2.1 Create `aur_python_packer/utils.py` and implement `run_command`.
- [ ] 2.2 Implement real-time merged stdout/stderr streaming to logging at `DEBUG` level.
- [ ] 2.3 Implement environment override logging (log only the `env` dict passed).
- [ ] 2.4 Implement error handling that logs the command failure and exit code.

## 3. Manager Refactoring

- [ ] 3.1 Replace all `print()` calls in `aur_python_packer/main.py` with `logger.info()` or `logger.debug()`.
- [ ] 3.2 Refactor `Manager.build_all` to use `run_command` for the pacman sync step.
- [ ] 3.3 Add logging for build order and package skip decisions.

## 4. Builder Refactoring

- [ ] 4.1 Update `aur_python_packer/builder.py` to use `logger` instead of `print`.
- [ ] 4.2 Replace `subprocess.run` calls in `execute_chroot_build` and `execute_local_build` with `run_command`.
- [ ] 4.3 Ensure build process output is logged to the file (DEBUG) and terminal (if INFO level requested for build).

## 5. Resolver and Generator Refactoring

- [ ] 5.1 Refactor `aur_python_packer/resolver.py` to use logging and `run_command` for `pacman -Si` and `git clone`.
- [ ] 5.2 Refactor `aur_python_packer/generator.py` to use logging and `run_command` for `makepkg --printsrcinfo`.
- [ ] 5.3 Refactor `aur_python_packer/repo.py` to use logging and `run_command` for `repo-add`.

## 6. Verification

- [ ] 6.1 Run the tool and verify the `logs/` directory and timestamped log file are created.
- [ ] 6.2 Verify that terminal output shows high-level progress.
- [ ] 6.3 Verify that the log file contains detailed command outputs and environment overrides.
- [ ] 6.4 Run tests and ensure no regressions in functionality.
