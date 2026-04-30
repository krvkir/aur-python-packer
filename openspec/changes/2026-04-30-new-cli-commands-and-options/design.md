# Design: New CLI Commands and Options

## Component Changes

### 1. `Manager` and `Sandbox` Integration
- All `git` operations will be executed using `Manager.run_in_sandbox` to ensure consistency and use the chroot-provided `git` binary.

### 2. `git-init` Implementation
- Iterate through `packages/` and `aur_packages/`.
- If `.git` directory doesn't exist:
  - Run `git init`.
  - Add `PKGBUILD`, `.SRCINFO`, and any other existing files.
  - Create initial commit: "Initial package generation/clone".

### 3. `git-show` Implementation
- Iterate through `packages/` and `aur_packages/`.
- Run `git diff --name-only PKGBUILD`.
- If output is non-empty, the package has uncommitted changes. List the package name.

### 4. Dependency Injection (`-d` Option)
- **`cli.py`**: Update `build` command to accept `multiple=True` for `--depends`.
- **`DependencyResolver`**: Add a method `inject_dependency(target_pkg, dep_name)` which adds an edge in the graph from the target package to the new dependency.
- **`Manager`**: Call `resolver.inject_dependency` before starting the build loop.
- **State Recording**: Store the list of injected dependencies in the package's entry in `build_index.json`.

## Technical Details
- Use `git config --global user.email "aur-packer@localhost"` and `git config --global user.name "AUR Packer"` inside the sandbox if not already configured.
- Ensure `git-show` correctly handles directories that are not yet git repos (e.g. by skipping them or warning).
