# Tasks: Smart Resolver

- [x] Implement `check_provides` logic using `pacman` to find packages providing a virtual name. <!-- id: 0 -->
- [x] Refactor `DependencyResolver.resolve` to follow the 4-tier search sequence. <!-- id: 1 -->
- [x] Move AUR cloning logic from `Manager` to `DependencyResolver`. <!-- id: 2 -->
- [x] Update `DependencyResolver` to parse the newly cloned AUR PKGBUILD/SRCINFO immediately after cloning. <!-- id: 3 -->
- [x] Ensure that once an AUR repo is cloned, it is treated as a "local" package in subsequent resolution steps. <!-- id: 4 -->
- [x] Add unit tests for "Provides" resolution. <!-- id: 5 -->
- [x] Add unit tests for the updated search priority. <!-- id: 6 -->
