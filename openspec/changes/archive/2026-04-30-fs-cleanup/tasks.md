# Tasks: File System Cleanup

- [x] Update `Manager.__init__` in `main.py` with new path definitions. <!-- id: 0 -->
- [x] Update `RepoManager` paths to use `local_repo/` and `srv/` subdirectories. <!-- id: 1 -->
- [x] Update `DependencyResolver` to use `packages/`, `aur_packages/`, and root `pypi_mapping.json`. <!-- id: 2 -->
- [x] Update `Builder` to use `srv/root/` for the chroot. <!-- id: 3 -->
- [x] Update `setup_logging` in `logger.py` to use the `logs/` directory. <!-- id: 4 -->
- [x] Update `cli.py` to ensure it passes the workspace directory correctly to all components. <!-- id: 5 -->
- [x] Verify directory creation logic in `Manager`. <!-- id: 6 -->
- [x] Update existing tests to reflect new directory structure. <!-- id: 7 -->
