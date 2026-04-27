## Why

The current build system relies on host-level tools (`extra-x86_64-build`, `buildpkg`) that require `sudo` and are distro-specific. This causes failures in environments with restricted permissions and makes the tool harder to use consistently across different Arch-based distributions.

## What Changes

- **BREAKING**: Removed reliance on `extra-x86_64-build` and `buildpkg`.
- **BREAKING**: Removed `extra-x86_64-build` and `buildpkg` detection logic.
- **BREAKING**: Removed `--local` flag as all builds will now be isolated by default.
- Introduced a unified rootless builder using `bwrap` (Bubblewrap) for isolated, clean environment builds without `sudo`.
- Added automated bootstrapping of a minimal build root in the `work` directory.

## Capabilities

### New Capabilities
- `rootless-isolated-build`: Provides a unified, clean, and rootless build environment using `bwrap` and a bootstrapped root.

### Modified Capabilities
- `chroot-builder`: Replaced distro-specific chroot tools with the unified rootless builder.
- `cli-interface`: Removed `--local` flag and updated default behavior to use rootless isolation.

## Impact

- `aur_python_packer/builder.py`: Major refactoring to implement `bwrap` logic and remove old builders.
- `aur_python_packer/main.py`: Updated to use the new builder and remove `sudo` from lifecycle commands.
- `aur_python_packer/cli.py`: Updated to remove the `--local` flag.
- `openspec/specs/chroot-builder/spec.md`: Updated to reflect unified rootless building.
- `openspec/specs/cli-interface/spec.md`: Updated to reflect removed flags.
