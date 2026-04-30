# Design: Smart Builder and Fallbacks

## Component Changes

### 1. `Builder` (`aur_python_packer/builder.py`)
- No major changes needed to the `build` method itself, but it should return information about whether it succeeded and how.

### 2. `StateManager` (`aur_python_packer/state.py`)
- Update `update_package` to accept a `skipped_checks` boolean parameter.
- Store this boolean in the package's entry in `build_index.json`.

### 3. `Manager` (`aur_python_packer/main.py`)
- Update the build loop in `build_all` to implement the retry logic:
  ```python
  try:
      # Try normal build
      pkg_file = self.builder.build(..., nocheck=nocheck)
      self.state.update_package(pkg, version, "success", skipped_checks=nocheck)
  except BuildError:
      if not nocheck:
          logger.info(f"Build failed, retrying {pkg} with --nocheck...")
          try:
              pkg_file = self.builder.build(..., nocheck=True)
              self.state.update_package(pkg, version, "success", skipped_checks=True)
          except BuildError:
              self.state.update_package(pkg, "failed", "error")
      else:
          self.state.update_package(pkg, "failed", "error")
  ```

### 4. CLI Interface (`aur_python_packer/cli.py`)
- Ensure the `--nocheck` flag is passed down to `Manager.build_all`.
- When the global flag is set, it overrides the local retry logic (it's always `--nocheck`).
