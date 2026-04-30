# Tasks: Smart Resolver

- [ ] Implement `check_provides` logic using `pacman` to find packages providing a virtual name. <!-- id: 0 -->
- [ ] Refactor `DependencyResolver.resolve` to follow the 4-tier search sequence. <!-- id: 1 -->
- [ ] Move AUR cloning logic from `Manager` to `DependencyResolver`. <!-- id: 2 -->
- [ ] Update `DependencyResolver` to parse the newly cloned AUR PKGBUILD/SRCINFO immediately after cloning. <!-- id: 3 -->
- [ ] Ensure that once an AUR repo is cloned, it is treated as a "local" package in subsequent resolution steps. <!-- id: 4 -->
- [ ] Add unit tests for "Provides" resolution. <!-- id: 5 -->
- [ ] Add unit tests for the updated search priority. <!-- id: 6 -->
