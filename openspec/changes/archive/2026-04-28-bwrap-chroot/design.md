## Context

Currently, `aur-python-packer` uses `extra-x86_64-build` (Arch) or `buildpkg` (Manjaro) for chroot builds. These tools require `sudo` and a pre-configured system-level chroot. In restricted environments (like CI or shared servers), this is often impossible. The current `--local` mode is a fallback that builds on the host, which is not hermetic and still struggles with `sudo` for dependency installation.

## Goals / Non-Goals

**Goals:**
- Implement a unified, rootless build system using `bwrap`.
- Ensure builds are clean/hermetic by using a bootstrapped root filesystem.
- Remove all requirements for `sudo` during the package lifecycle (sync, build, repo-add).
- Simplify the tool by having one robust build path instead of distro-specific fallbacks.

**Non-Goals:**
- Supporting kernels without user namespace support (it is a hard requirement).
- Cross-architecture builds (e.g., building ARM on x86).
- Building for non-Arch-based distributions.

## Decisions

### Decision 1: Use `bwrap` (Bubblewrap) for Isolation
- **Rationale**: `bwrap` is the standard for unprivileged sandboxing on Linux (used by Flatpak). It allows mapping the current user to `uid 0` inside a namespace, enabling `pacman` to perform "root" operations within a confined directory.
- **Alternatives**:
  - `systemd-nspawn`: Requires root to set up namespaces/cgroups.
  - `podman`: Not installed on the target system and heavier dependency.
  - `proot`: Slower (ptrace-based) and not installed.

### Decision 2: Minimal Root Bootstrapping
- **Rationale**: To guarantee a clean environment, we will use `pacman --root` to install `base-devel` into a local directory (`work/root`). This ensures host packages don't contaminate the build.
- **Alternatives**:
  - `pacstrap`: Requires `sudo`.
  - Bind-mounting host `/`: Doesn't provide a clean environment; risk of host contamination.

### Decision 3: Sudo Shim for `makepkg`
- **Rationale**: `makepkg -s` internally calls `sudo pacman`. Since we are "root" inside the `bwrap` namespace, we can't use real `sudo`. We will provide a shim in the sandbox's `PATH` that simply shifts arguments and executes them.
- **Alternatives**:
  - `makepkg --asdeps`: Still requires `pacman` to be available and often expects `sudo`.

### Decision 4: Custom `pacman.conf` for all operations
- **Rationale**: All `pacman` operations (sync, install) must use a config that overrides `DBPath`, `CacheDir`, etc., to point into the `work` directory to avoid permission errors on `/var`.

## Risks / Trade-offs

- **[Risk] Disk Space** → The bootstrapped root adds ~400MB to the `work` directory. *Mitigation*: Provide a command or documentation for cleaning up the work directory.
- **[Risk] Performance** → Initial bootstrap is slow (~2-5 minutes depending on internet). *Mitigation*: The root is persistent and reused across builds.
- **[Risk] User Namespace Availability** → Some hardened kernels disable unprivileged user namespaces. *Mitigation*: Check for `/proc/sys/kernel/unprivileged_userns_clone` or test `unshare` at startup and provide a clear error message.
