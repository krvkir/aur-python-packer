## 1. Environment Setup

- [x] 1.1 Add `py-dagviz = "^0.1.0"` to `pyproject.toml` (corrected from `dagviz` which is SVG-only)
- [x] 1.2 Run `poetry install` to update the virtual environment

## 2. Core Implementation

- [x] 2.1 Create `aur_python_packer/graph_utils.py` for graph processing
- [x] 2.2 Implement `print_dependency_graph` to map `networkx` nodes to status-aware labels
- [x] 2.3 Implement color injection logic for terminal output using `re.sub` and `click.style`
- [x] 2.4 Update `aur_python_packer/cli.py` to call `print_dependency_graph` in the `resolve` command

## 3. Verification

- [x] 3.1 Verify DAG visualization with complex package dependencies
- [x] 3.2 Verify `[built]` markers reflect the state in `build_index.json`
- [x] 3.3 Verify automatic color stripping when output is piped (e.g., `resolve pkg | cat`)
