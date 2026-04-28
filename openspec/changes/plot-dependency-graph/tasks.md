## 1. Environment Setup

- [ ] 1.1 Add `dagviz = "^0.2.0"` to `pyproject.toml`
- [ ] 1.2 Run `poetry install` to update the virtual environment

## 2. Core Implementation

- [ ] 2.1 Create `aur_python_packer/graph_utils.py` for graph processing
- [ ] 2.2 Implement `print_dependency_graph` to map `networkx` nodes to status-aware labels
- [ ] 2.3 Implement color injection logic for terminal output using `re.sub` and `click.style`
- [ ] 2.4 Update `aur_python_packer/cli.py` to call `print_dependency_graph` in the `resolve` command

## 3. Verification

- [ ] 3.1 Verify DAG visualization with complex package dependencies
- [ ] 3.2 Verify `[built]` markers reflect the state in `build_index.json`
- [ ] 3.3 Verify automatic color stripping when output is piped (e.g., `resolve pkg | cat`)
