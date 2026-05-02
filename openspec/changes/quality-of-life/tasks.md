## 1. Core Infrastructure & Workspace

- [ ] 1.1 Relocate sandboxed home directory from `<workdir>/home` to `<workdir>/srv/home` in `Sandbox` and `Manager`
- [ ] 1.2 Modify `run_command` in `utils.py` to accept an optional `msg` parameter for INFO-level logging
- [ ] 1.3 Update `Sandbox.run` and `Sandbox.run_host_command` in `sandbox.py` to construct descriptive environment summaries (e.g., "[Sandbox: shared-net]")
- [ ] 1.4 Update `Manager.run_in_sandbox` in `main.py` to use environment summaries when calling the sandbox

## 2. Dependency Resolution & Logging

- [ ] 2.1 Refine tier classification in `resolver.py` to ensure packages in `aur_packages/` are strictly assigned the `aur` tier
- [ ] 2.2 Remove redundant "Starting sandboxed build for..." log message in `builder.py`
- [ ] 2.3 Verify that sandboxed commands show concise summaries at INFO level and full `bwrap` details at DEBUG level

## 3. Visualization & CLI

- [ ] 3.1 Implement node filtering in `graph_utils.py` to omit `repo` tier dependencies when node count > 20
- [ ] 3.2 Add "Omitted N repository dependencies" notice to graph output when filtering is active
- [ ] 3.3 Add `--show-repo-deps` flag to `build` and `resolve` commands in `cli.py`
- [ ] 3.4 Pass `show_repo_deps` flag from CLI through `Manager` to `print_dependency_graph`

## 4. Git Integration Improvements

- [ ] 4.1 Update `_git_init_in_dir` in `main.py` to fetch `user.name` and `user.email` from host global Git config using `subprocess`
- [ ] 4.2 Refactor `Manager.git_show_changed` in `main.py` to be a generator yielding package names
- [ ] 4.3 Update `git_show` command in `cli.py` to iterate over the generator and print results immediately
