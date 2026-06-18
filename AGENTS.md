# AGENTS.md — AUR Python Packer

## Project Overview

A CLI tool that automates the full lifecycle of AUR Python packages: recursive
dependency resolution across repos/AUR/PyPI, isolated builds via bubblewrap,
and local repository management. Built for Arch/Manjaro.

## Build & Test Commands

```bash
# Install (first time or after dependency changes)
poetry install

# Run the tool
poetry run aur-python-packer --help

# Unit tests (all files matching tests/test_*.py)
make unit-test
# or directly:
poetry run pytest tests/test_*.py

# Integration tests (requires actual build environment)
make integration-test

# Full test suite
make test

# Clean build artifacts
make clean
```

## Project Structure

```
aur_python_packer/   # Source package (NOT src/)
  cli.py             # Click CLI entrypoint
  main.py            # Manager orchestrator
  resolver.py        # 4-tier dep resolution (local→repos→AUR→PyPI)
  generator.py       # PKGBUILD generation from PyPI metadata
  builder.py         # Isolated builds via bubblewrap
  sandbox.py         # bwrap sandbox & sudo shim
  repo.py            # Local pacman repository
  state.py           # Build state (build_index.json)
  clients.py         # AUR RPC & PyPI API clients
  metadata.py        # SRCINFO & PKGBUILD parsing
  audit.py           # .SRCINFO generation
  cache.py           # Network response cache
  graph_utils.py     # Terminal DAG visualization
  utils.py, config.py, logger.py  # Utilities, config, logging
  templates/         # Jinja2 PKGBUILD templates
tests/               # Pytest test suite (test_*.py)
openspec/            # Spec-driven development artifacts
  specs/             # Current capability specs (markdown)
  changes/           # Active proposals
  changes/archive/   # Completed changes
  config.yaml        # OpenSpec configuration
Makefile             # Common task shortcuts
```

## Development Workflow (OpenSpec)

Spec-driven development with OpenSpec:

1. **Propose**: Create `openspec/changes/<name>/` with `proposal.md`,
   `design.md`, `specs/`, `tasks.md`.
2. **Implement**: Work through `tasks.md`. Tests go in `tests/`.
3. **Archive**: Move to `changes/archive/`, merge specs into `openspec/specs/`.

Live specs use GIVEN/WHEN/THEN scenarios to describe behavior.

## Code Conventions

- **Python 3.14+** with **Poetry**. Source in `aur_python_packer/` (flat package).
- CLI via **Click**: `@cli.command()` decorators in `cli.py`.
- `Manager` is the top-level orchestrator; all subsystems are composed there.
- Use `setup_logging(workdir)` early in commands — it returns the log file path.
- Test files match `tests/test_*.py`. One test file per source module.
- Architecture: Manager → Resolver, Generator, Builder, RepoManager.

## Key Dependencies

- `click ^8.1` — CLI framework
- `networkx ^3.2` — dependency graph and topological sort
- `jinja2 ^3.1` — PKGBUILD template rendering
- `requests ^2.31` — AUR RPC and PyPI API calls
- `packaging ^23.2` — version parsing
- `py-dagviz ^0.1.0` — graph visualization
- `bubblewrap` (system) — rootless sandboxed builds
- `pacman >= 7.1` (system) — package management

## Boundaries

- **Do not** modify `openspec/changes/archive/` (historical records).
- **Do not** change `pyproject.toml` version or build-system without instruction.
- **Do** add/update tests for any behavioral change. Run `make test` before
  considering work complete.
- **Do** preserve Manager-as-orchestrator: subsystems shouldn't call each other.
- `.orig`, `.rej`, `*~` files are safe to clean up. `*.org` files are user dev
  journals — agents should not modify them.
