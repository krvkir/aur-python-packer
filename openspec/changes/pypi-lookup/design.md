## Context

The current dependency resolution logic relies on a naive prefix check (`python-`) to decide if a package is sourced from PyPI. This leads to false positives and misses transitive dependencies. The `PyPIGenerator` also fails to extract dependencies from the PyPI JSON API, resulting in manual effort to fix `PKGBUILD` files.

## Goals / Non-Goals

**Goals:**
- Implement exact-match verification against the PyPI JSON API.
- Automatically extract and parse dependencies from PyPI metadata.
- Standardize the mapping between PyPI project names and Arch Linux package names.
- Use a robust library (`packaging`) for parsing dependency specifications.

**Non-Goals:**
- Implementing keyword-based search (only exact lookups for identified dependencies).
- Implementing a persistent local cache for PyPI metadata (stateless for now).
- Handling non-Python dependencies found in PyPI metadata (focus on Python packages).

## Decisions

- **Decision 1: Use `packaging` library for PEP 508 requirements**
  - **Rationale**: Parsing requirement strings like `requests[security] >= 2.21.0; python_version < '3.8'` is complex. The `packaging` library is the industry standard for this task.
  - **Alternatives**: Custom regex patterns (would be fragile and incomplete).

- **Decision 2: Integrate PyPI lookup into `DependencyResolver`**
  - **Rationale**: The resolver is the central point for identifying where a package comes from. Moving the check here allows it to stop "guessing" based on prefixes.
  - **Alternatives**: Checking PyPI only during the generation phase (too late, as sub-dependencies wouldn't be resolved).

- **Decision 3: Name Mapping Convention**
  - **Rationale**: PyPI names are case-insensitive and can use underscores/hyphens. Arch packages are typically `python-<lowered-name>`. We will use the PyPI-provided `info.name` as the source of truth, normalized to lowercase for Arch.
  - **Example**: `FastMCP` (PyPI) -> `python-fastmcp` (Arch).

## Risks / Trade-offs

- **[Risk]** Excessive API calls to PyPI during deep dependency trees.
  - **Mitigation**: The `DependencyResolver` already uses a `visited` set to prevent redundant lookups. We will ensure one API call per unique package.
- **[Risk]** Package names on PyPI differing significantly from Arch/AUR names.
  - **Mitigation**: The resolver checks local, repo, and AUR *before* PyPI. PyPI is the last resort. We will prioritize Arch-specific naming where possible.
