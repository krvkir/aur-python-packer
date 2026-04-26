# Tasks: Manjaro Chroot Implementation

- [ ] Update `aur_python_packer/builder.py` to include `chrootbuild` in `check_chroot_tools`.
- [ ] Update `execute_chroot_build` to handle `chrootbuild` specific flags if they differ from `buildpkg`.
- [ ] Add unit tests for tool selection on Manjaro.
- [ ] Verify `chrootbuild` execution logic on a Manjaro environment (or mock it).
