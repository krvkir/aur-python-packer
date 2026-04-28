## 1. Environment Setup

- [x] 1.1 Add `py-dagviz = "^0.1.0"` to `pyproject.toml`
- [x] 1.2 Run `poetry install` to update the virtual environment

## 2. Core Implementation

- [x] 2.1 Create `aur_python_packer/graph_utils.py` for graph processing
- [x] 2.2 Implement `print_dependency_graph` to map `networkx` nodes to status-aware labels
- [x] 2.3 Implement color injection logic for terminal output using `re.sub` and `click.style`
- [x] 2.4 Update `aur_python_packer/cli.py` to call `print_dependency_graph` in the `resolve` command

## 3. Enhancements

- [x] 3.1 Update `graph_utils.py` to handle "failed" status and colorize it in red
- [x] 3.2 Update `cli.py` to catch `ValueError` from resolver and print a clean error message
- [x] 3.3 Update `Manager.build_all` in `main.py` to display the dependency graph before starting
- [x] 3.4 Update `Manager.build_all` in `main.py` to display the dependency graph after each successful build

## 4. Verification

- [x] 4.1 Verify "failed" status is correctly displayed and colorized in the graph
- [x] 4.2 Verify unresolvable packages are reported gracefully without traceback
- [x] 4.3 Verify graph is shown at the start and during the build process
