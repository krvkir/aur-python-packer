## Why

Dependency resolution output is currently a flat list, which makes it difficult to understand complex relationships in a Directed Acyclic Graph (DAG) and to identify which parts of the dependency tree are already satisfied by local builds.

## What Changes

- Implement a graphical DAG representation in the terminal for the `resolve` command.
- Annotate the graph with package tiers and build status.
- Add support for ANSI colors with automatic stripping for non-TTY outputs.

## Capabilities

### New Capabilities
- (None)

### Modified Capabilities
- `user-interaction-interface`: Add requirements for graphical dependency visualization and status indication.

## Impact

- CLI: The `resolve` command will now output a graph before the build sequence list.
- Dependencies: Add `dagviz` to handle ASCII/Unicode DAG rendering.
- Codebase: New utility for graph transformation and rendering.
