# Design: Manjaro Chroot Integration

## Architecture
The `Builder` class in `aur_python_packer/builder.py` will be updated to refine its tool selection logic.

### OS Detection
The `detect_os` method already checks for `/etc/manjaro-release`. We will ensure this is robust.

### Tool Selection
1. If `os_type == "manjaro"`:
   - Check for `chrootbuild` availability.
   - If available, use it for chroot builds.
   - Fallback to `buildpkg` or local `makepkg` if `chrootbuild` is missing but requested.

### Execution Flow
For Manjaro:
- Command: `chrootbuild -p <pkgname>` (or appropriate flags for `chrootbuild`).
- Note: `buildpkg` is also a common tool on Manjaro; we should clarify if `chrootbuild` is specifically desired over `buildpkg` or if they should be alternatives. Given the prompt, we prioritize `chrootbuild`.
