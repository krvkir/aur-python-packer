## Context

The system needs to identify all local AUR packages and their dependencies to build a dependency graph. Since `PKGBUILD` files are Bash scripts, extracting information reliably requires handling Bash variable syntax and list structures.

## Goals / Non-Goals

**Goals:**
- Recursively find all `PKGBUILD` files in a given root directory.
- Extract `pkgname`, `pkgver`, `depends`, `makedepends`, and `checkdepends`.
- Handle simple variable expansions used in dependency lists.
- Detect and report duplicate package names across different directories.

**Non-Goals:**
- Performing the actual build of packages.
- Resolving dependencies against the AUR or official repositories (handled by the Resolver).
- Full emulation of complex Bash scripts within `PKGBUILD`s.

## Decisions

### 1. Metadata Extraction via Sourcing
**Decision**: Use a subshell to source the `PKGBUILD` and print the required variables as JSON.
**Rationale**: Regex parsing of Bash lists and variable expansions is brittle and complex. Sourcing the file allows Bash itself to handle the syntax.
**Alternative**: Pure regex parsing. Rejected due to inability to handle variable expansion like `${_pyname}` or multi-line list definitions.

### 2. Output Data Structure
**Decision**: Represent the local repository as a dictionary where keys are `pkgname` and values are objects containing `path`, `version`, and `dependencies`.
**Rationale**: Provides O(1) lookup for package availability during resolution.

### 3. Implementation Language
**Decision**: Python 3.
**Rationale**: Excellent library support for JSON, path manipulation, and subprocess management.

## Risks / Trade-offs

- **Risk**: Sourcing `PKGBUILD` files executes code, which could be dangerous if the files are from an untrusted source.
- **Mitigation**: This tool is intended for use by a developer on their own local collection of `PKGBUILD`s. We will document that only trusted directories should be scanned.
- **Risk**: Performance of spawning a `bash` process for every `PKGBUILD`.
- **Mitigation**: The number of local packages (JupyterAI stack) is expected to be < 100, so the overhead is negligible.
