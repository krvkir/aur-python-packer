# Proposal: Use chrootbuild for Manjaro

## Problem Statement
Currently, the system uses standard `makepkg` or `extra-x86_64-build` logic which might not be optimal for Manjaro users who prefer `chrootbuild` (from `manjaro-tools-pkg`) for clean chroot builds. We need to ensure that when Manjaro is detected, the preferred Manjaro tooling is used.

## Proposed Change
Modify the build execution logic to prioritize `chrootbuild` when the host system is identified as Manjaro.

## Goals
- Detect Manjaro Linux correctly.
- Use `chrootbuild` for building packages in a chroot environment on Manjaro.
- Maintain backward compatibility for Arch Linux users.
