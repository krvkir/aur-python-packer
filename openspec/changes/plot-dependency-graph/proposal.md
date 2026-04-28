## Why

Dependency resolution output is currently a flat list, which makes it difficult to understand complex relationships in a Directed Acyclic Graph (DAG) and to identify which parts of the dependency tree are already satisfied by local builds.

## What Changes

- Implement a graphical DAG representation in the terminal for the `resolve` command.
- Annotate the graph with package tiers and build status (including success and failure).
- Add support for ANSI colors with automatic stripping for non-TTY outputs.
- Show the dependency graph before and during the build process to provide real-time status updates.
- Improve error handling in the dependency resolver to provide user-friendly messages for unresolvable packages.

## Capabilities

### New Capabilities
- (None)

### Modified Capabilities
- `user-interaction-interface`: Add requirements for graphical dependency visualization and status indication.

## Impact

- CLI: The `resolve` command will now output a graph before the build sequence list.
- Build Loop: The build process will display the graph to show progress.
- Dependencies: Add `dagviz` to handle ASCII/Unicode DAG rendering.
- Codebase: New utility for graph transformation and rendering.
