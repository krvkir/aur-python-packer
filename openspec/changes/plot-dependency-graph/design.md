## Context

The current `resolve` command provides a flat list of dependencies. To improve user experience, we need a graphical representation of the dependency Directed Acyclic Graph (DAG).

## Goals / Non-Goals

**Goals:**
- Provide a clear, graphical visualization of the dependency DAG in the terminal.
- Indicate which packages are already built.
- Use colors to enhance readability in interactive sessions.
- Ensure colors are stripped when output is redirected (e.g., to a file or an LLM).

**Non-Goals:**
- Interactive graph exploration (e.g., TUI).
- Exporting the graph to external formats (e.g., SVG/PDF) in this phase.

## Decisions

### Use `dagviz` for DAG rendering
**Rationale**: `dagviz` is a lightweight Python library specifically designed for rendering `networkx` DiGraphs as ASCII/Unicode DAGs in the terminal. It handles complex edge crossings better than a simple tree printer.
**Alternatives Considered**:
- Manual tree printer: Simple to implement but fails to correctly represent DAGs (duplicates shared nodes or misses edges).
- `Graphviz`: Powerful but requires external binaries (`dot`), which adds deployment complexity.

### Post-processing for Colorization
**Rationale**: `dagviz` calculates layout based on string length. If ANSI escape codes are inserted into the labels before rendering, `dagviz` may miscalculate the layout. By post-processing the final ASCII string using regex to inject colors, we preserve the layout integrity.
**Alternatives Considered**:
- Pre-colorization: Risk of corrupted ASCII art if `dagviz` doesn't handle ANSI codes.

### Automatic Color Stripping
**Rationale**: Using `click.style` and `click.echo(color=...)` ensures that colors are only shown in supporting terminals. This is crucial for automation environments and LLM interactions where ANSI codes cause clutter.

## Risks / Trade-offs

- [Risk] Wide Graphs → [Mitigation] `dagviz` is generally compact, but very deep/wide graphs may still wrap. We will rely on terminal wrapping or user resizing.
- [Risk] Unicode Support → [Mitigation] Use `round_angle=True` for better visuals but provide a way to fallback to pure ASCII if needed (non-goal for now, but `dagviz` supports it).
