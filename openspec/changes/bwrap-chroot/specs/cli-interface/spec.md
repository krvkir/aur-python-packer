## REMOVED Requirements

### Requirement: Local Build Flag
**Reason**: All builds are now isolated via `bwrap` by default. The tool no longer supports non-isolated host builds.
**Migration**: Remove `--local` from command line invocations.
