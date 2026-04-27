## 1. Preparation and Cleanup

- [ ] 1.1 Remove `detect_os` and `check_chroot_tools` from `aur_python_packer/builder.py`
- [ ] 1.2 Remove `--local` option from `aur_python_packer/cli.py`
- [ ] 1.3 Update `Manager.__init__` in `aur_python_packer/main.py` to remove `local_only` parameter

## 2. Rootless Infrastructure

- [ ] 2.1 Implement `Builder._bootstrap_root()` to initialize `work/root` using `pacman --root`
- [ ] 2.2 Implement `Builder._generate_sudo_shim()` to create a `sudo` script in `work/bin`
- [ ] 2.3 Implement `Builder._run_in_sandbox()` using `subprocess.run` and `bwrap` command
- [ ] 2.4 Update `RepoManager.generate_custom_conf` to include `LogFile` and `GPGDir` overrides

## 3. Core Builder Refactoring

- [ ] 3.1 Rewrite `Builder.build` to always use the rootless sandbox
- [ ] 3.2 Implement `Builder.execute_sandboxed_build` (replacing `execute_chroot_build` and `execute_local_build`)
- [ ] 3.3 Ensure the sandbox correctly bind-mounts `work/root`, package directory, and local repository

## 4. Manager and CLI Integration

- [ ] 4.1 Remove `sudo` from the `pacman -Sy` call in `Manager.build_all`
- [ ] 4.2 Update `Manager` to use the custom `pacman.conf` for all database synchronization
- [ ] 4.3 Verify that build artifacts are correctly moved to the local repository after a sandboxed build

## 5. Verification

- [ ] 5.1 Verify that `aur-python-packer` can build a simple package without `sudo`
- [ ] 5.2 Verify that `work/root` is correctly populated on the first run
- [ ] 5.3 Verify that dependencies are correctly installed into the sandbox during the build
