## Context

The `aur-python-packer` tool is functional but suffers from "UI/UX debt" in its terminal output and workspace organization. Specifically, the Bubblewrap command logging is too verbose for general use, and large dependency graphs are difficult to read in standard terminal sizes. Additionally, some internal state is bleeding into the workspace root.

## Goals / Non-Goals

**Goals:**
- Sanitize sandboxed command logs by hiding infrastructure details (`bwrap` flags).
- Improve readability of dependency graphs through conditional filtering.
- Align workspace structure with the principle of least clutter by moving `home/` to `srv/`.
- Ensure AUR packages maintain their identity throughout the lifecycle.
- Improve CLI responsiveness for git-based status checks.

**Non-Goals:**
- Changing the underlying sandbox technology (Bubblewrap).
- Modifying the core dependency resolution algorithm itself (only the classification logic).
- Adding full-featured Git management (just improving the existing shim commands).

## Decisions

### 1. Summary-based Sandbox Logging
We will modify the internal `run_command` utility to support an optional `msg` string. When provided, this message will be logged at the `INFO` level, while the raw command (including all `bwrap` flags) will be logged at `DEBUG`.
- **Rationale**: Users need to know *what* is running (e.g., "Executing makepkg in sandbox"), not how the sandbox is constructed.
- **Alternatives**: Filtering the `bwrap` command string via regex, but this is brittle. A dedicated summary parameter is cleaner.

### 2. Conditional Graph Filtering
In `graph_utils.py`, we will implement a filter that removes nodes with `tier == "repo"` if the total node count exceeds 20.
- **Rationale**: Repository dependencies are "leaves" that don't require building; they are the primary source of bloat in large graphs.
- **Alternatives**: Collapsing repo nodes into a single "Official Repos" node, but filtering is simpler and more effective for visibility.

### 3. Persistent Host Git Identity
Instead of hardcoding "AUR Packer", the `git_init` logic will query the host's `git config --global user.name` and `email`.
- **Rationale**: Makes generated/cloned packages feel like they belong to the user, facilitating easier upstreaming if desired.
- **Alternatives**: Adding CLI flags for user/email, but auto-detection is more convenient.

### 4. Streaming Git Status
`Manager.git_show_changed` will be refactored into a generator. The CLI will print each package as it is identified.
- **Rationale**: Large workspaces can make `git-show` feel "stuck" while it iterates through many directories. Streaming provides immediate feedback.

## Risks / Trade-offs

- **[Risk]** Missing context in logs → **[Mitigation]** The full command is always preserved in the file-based `DEBUG` log.
- **[Risk]** Confusion over missing graph nodes → **[Mitigation]** Print a notice when nodes are omitted (e.g., "Note: Omitted 15 repository dependencies...").
- **[Risk]** Broken workspace migration → **[Mitigation]** The tool will check both old and new `home` locations or simply recreate the ephemeral home in `srv/`.
