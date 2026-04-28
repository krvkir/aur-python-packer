## Context

The current `resolve` command provides a flat list of dependencies. To improve user experience, we need a graphical representation of the dependency Directed Acyclic Graph (DAG) and better error handling for resolution failures.

## Goals / Non-Goals

**Goals:**
- Provide a clear, graphical visualization of the dependency DAG in the terminal.
- Indicate which packages are already built (success) or failed.
- Use colors to enhance readability in interactive sessions.
- Ensure colors are stripped when output is redirected.
- Display progress visually during the build process.
- Handle resolution errors gracefully without crashing.

**Non-Goals:**
- Interactive graph exploration (e.g., TUI).

## Decisions

### Use `dagviz` for DAG rendering
**Rationale**: `dagviz` is a lightweight Python library specifically designed for rendering `networkx` DiGraphs as ASCII/Unicode DAGs in the terminal.

### Post-processing for Colorization
**Rationale**: `dagviz` calculates layout based on string length. If ANSI escape codes are inserted into the labels before rendering, `dagviz` may miscalculate the layout.

### Automatic Color Stripping
**Rationale**: Using `click.style` and `click.echo(color=...)` ensures that colors are only shown in supporting terminals.

### Build Loop Integration
**Rationale**: Printing the graph at the start of `build_all` and after each successful build provides immediate visual feedback on progress and dependencies.

### Graceful Error Handling
**Rationale**: Catching `ValueError` from the resolver in the CLI layer allows us to present a clean "Package not found" message instead of a traceback.

## Risks / Trade-offs

- [Risk] Wide Graphs → [Mitigation] `dagviz` is generally compact, but very deep/wide graphs may still wrap.
- [Risk] Unicode Support → [Mitigation] Use `round_angle=True` for better visuals.
