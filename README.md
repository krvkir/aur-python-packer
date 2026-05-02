# AUR Python Packer

Automated AUR Package Lifecycle Manager for Python.

``` bash
$ poetry run aur-python-packer resolve jupyter-ai         
Resolving dependencies for jupyter-ai...

Dependency Graph:
• jupyter-ai
└─• python-jupyter-ai (local) [built]
  ├─• python-jupyter-server-mcp (local) [built]
  │ └─• python-fastmcp (local) [built]
  │   ├─• python-py-key-value-aio (local) [built]
  │   │ └─• python-beartype (aur) [built]
  │   ├─• python-griffelib (aur) [built]
  │   ├─│─• python-mcp (aur) [built]
  │   │ │ ├─• python-sse-starlette (aur) [built (no checks)]
  │   │ │ ├─• python-httpx-sse (aur) [built]
  │   ├─┴─┴─• python-uv-dynamic-versioning (aur) [built]
  │   ├─• python-openapi-pydantic (aur) [built]
  │   ├─• python-cyclopts (aur) [built]
  │   │ ├─• python-docstring-parser (aur) [built]
  │   │ └─• python-rich-rst (aur) [built]
  │   ├─• python-jsonref (aur) [built]
  │   │ └─• python-pdm-pep517 (aur) [built]
  │   └─• python-uncalled-for (aur) [built]
  ├─• python-jupyter-ai-acp-client (local) [built]
  ├─│─• python-jupyter-ai-chat-commands (local) [built]
  │ ├─│─• python-agent-client-protocol (aur) [built]
  ├─┼─┼─• python-jupyter-ai-persona-manager (local) [built]
  ├─│─┼─┼─• python-jupyter-ai-router (local) [built]
  ├─┴─┴─┴─┴─• python-jupyterlab-chat (local) [built]
  │         ├─• python-rfc3987-syntax (local) [built]
  │         └─• python-bleach-git (local) [built]
  ├─• python-jupyter-server-documents (local) [built]
  ├─• python-jupyterlab-commands-toolkit (local) [built]
  │ └─• python-jupyterlab-eventlistener (local) [built]
  ├─• python-jupyterlab-notebook-awareness (local) [built]
  └─• python-jupyter-ai-tools (local) [built]
Note: Omitted 73 repository dependencies from visualization. Use --show-repo-deps to see full graph.

```

## The Problem
Managing Python packages on Arch Linux often requires a mix of official repositories, AUR packages, and occasionally generating new ones from PyPI. Keeping track of recursive dependencies across these tiers, building them in clean environments, and maintaining a local repository for subsequent builds is a manual and error-prone process.

## The Solution
`aur-python-packer` is a unified tool that automates the entire lifecycle of AUR-bound Python packages. It resolves dependencies recursively, generates missing `PKGBUILD` files from PyPI, and executes builds in an isolated, rootless sandbox.

## Features

### 🔍 Multi-Tier Dependency Resolution
The system resolves dependencies using a prioritized search sequence:
1.  **Local**: Checks for existing `PKGBUILD` files in your workspace.
2.  **Official Repos**: Searches standard Arch/Manjaro repositories (including "Provides" fields).
3.  **AUR**: Clones and parses AUR repositories via RPC if not found locally.
4.  **PyPI**: Falls back to querying PyPI and generating a package if it exists there.

### 🛡️ Isolated Sandboxed Builds
Builds are executed inside a **Bubblewrap (`bwrap`)** sandbox:
- **Rootless**: No host-level root privileges required.
- **Hermetic**: Isolated from the host filesystem to prevent contamination.
- **Sudo Shim**: Intercepts administrative calls within the sandbox to simulate privileged operations safely.

### 🏗️ Automatic Package Generation
When a dependency is only available on PyPI, the tool:
- Fetches metadata via the PyPI JSON API.
- Renders a functional `PKGBUILD` using a standardized Jinja2 template.
- Automatically handles checksum generation and `.SRCINFO` creation.

### 📦 Local Repository Management
Maintains a local `pacman` repository within the workspace:
- Built packages are automatically added to the repository.
- Subsequent builds in the same session utilize this repository to satisfy dependencies.
- Compatible with modern `pacman` versions (7.1+).

### 📊 Real-time Visualization
- Displays a Unicode/ANSI-colored **Dependency DAG** (Directed Acyclic Graph).
- Provides real-time updates on build progress and status directly in the terminal.

### 🛠️ Maintenance & Resilience
- **Smart Fallback**: Automatically retries builds with `--nocheck` if the initial build fails.
- **Git Integration**: Tracks manual modifications to generated `PKGBUILD`s using built-in Git support.
- **Dependency Injection**: Allows adding ad-hoc dependencies at runtime via the CLI.

---

## Installation

### Prerequisites
- **Arch Linux** or **Manjaro**
- `bubblewrap`
- `pacman` & `base-devel`
- `git`
- `python` (>= 3.14)
- `poetry`

### Setup
```bash
git clone https://github.com/krvkir/aur-python-packer.git
cd aur-python-packer
poetry install
```

---

## Usage

### Building a Package
Build a package and all its missing dependencies:
```bash
poetry run aur-python-packer build jupyter-ai
```

### Resolving Dependencies
Visualize the dependency tree without starting a build:
```bash
poetry run aur-python-packer resolve jupyter-ai
```

### Injecting Extra Dependencies
Force the tool to treat a package as a dependency of your target:
```bash
poetry run aur-python-packer build my-pkg -d python-setuptools-scm
```

### Git Management
Initialize git tracking for all newly cread packages:
```bash
poetry run aur-python-packer git-init

# Show which packages have uncommitted manual changes (both newly created and cloned from AUR)
poetry run aur-python-packer git-show
```

### Custom Workspace
Specify a custom directory for all artifacts and state:
```bash
poetry run aur-python-packer -w ./my-workspace build python-pkg
```

---

## Architecture & Working Principles

### Architecture
- **Orchestrator (`Manager`)**: Coordinates the lifecycle between resolution, generation, and building.
- **Dependency Resolver**: Implements the 4-tier lookup strategy and circular dependency detection using `networkx` for topological sorting.
- **PyPI Generator**: Uses Jinja2 templates to transform PyPI metadata into valid `PKGBUILD` files.
- **Isolated Builder**: Leverages `bwrap` to create a mount-namespace-isolated rootfs. It uses a custom `sudo` shim to allow `makepkg` to perform "privileged" installations within the sandbox.
- **Local Repository Manager**: Dynamically maintains a signed `pacman` repository database (`repo-add`) and generates custom `pacman.conf` overrides for the sandbox.

### Core Principles
- **Hermeticity**: Every build starts with a clean, synchronized state. Host configuration is never modified.
- **Persistence**: The tool maintains a rigid workspace structure:
  - `aur_packages/`: Local clones of AUR repositories.
  - `packages/`: Generated packages from PyPI.
  - `local_repo/`: The binary package repository and database.
  - `srv/`: Internal tool state (GPG keys, pacman DBs, and the build sandbox).
  - `logs/`: Concurrent logging to stdout (clean INFO) and file (detailed DEBUG).
- **Resilience**: State is tracked in `build_index.json`, allowing the tool to resume interrupted build sequences or skip already-built versions.
- **Modernity**: Specifically designed to handle `pacman` 7.1+ features and security requirements in isolated environments.

## Limitations
- **Platform Specific**: Strictly requires `pacman` and is designed for Arch-based distributions.
- **Python-Centric**: While it can handle general AUR packages, the generation logic is optimized for the Python ecosystem.
- **Environment**: Requires `bubblewrap` for isolation; cannot run in environments where unprivileged user namespaces are disabled.
