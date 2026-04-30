# Proposal: Smart Builder and Fallbacks

## Problem
Sometimes package builds fail due to non-critical test failures. Currently, the user has to manually re-run the build with `--nocheck`. Furthermore, there is no persistent record of whether a package was built with or without checks, which is important for quality tracking.

## Proposed Change
Implement an automated fallback mechanism in the builder and enhance state tracking.

### Automated Fallback:
If a regular build attempt fails, the system will automatically retry the build with the `--nocheck` flag. This simplifies the user experience by attempting to "just work" even if tests are flaky or incompatible with the environment.

### State Tracking:
All built packages will now be marked in the build index (`build_index.json`) with their check status:
- `skipped_checks: true` if built with `--nocheck`.
- `skipped_checks: false` if built normally.

### Global Skip:
If the user launches the tool with a global `--nocheck` flag, all packages built during that session will have checks skipped and will be marked as `skipped_checks: true` in the index.

## Impact
- **Resilience**: Increases the success rate of automated build runs.
- **Traceability**: Users can easily identify which packages were built without running tests.
- **Convenience**: Reduces manual intervention for common build issues.
