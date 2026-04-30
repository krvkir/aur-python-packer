# Tasks: Smart Builder and Fallbacks

- [ ] Update `StateManager.update_package` to support the `skipped_checks` field. <!-- id: 0 -->
- [ ] Implement retry logic in `Manager.build_all` to fallback to `--nocheck` on failure. <!-- id: 1 -->
- [ ] Ensure the global `--nocheck` CLI flag correctly influences all builds and state updates. <!-- id: 2 -->
- [ ] Add logging to clearly indicate when a fallback build is occurring. <!-- id: 3 -->
- [ ] Verify that successfully built packages with `skipped_checks: true` are correctly identified as "current" in subsequent runs. <!-- id: 4 -->
- [ ] Add unit tests for the retry logic and state recording. <!-- id: 5 -->
