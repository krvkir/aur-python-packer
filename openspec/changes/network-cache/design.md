## Context

The tool currently makes direct `requests.get()` calls to PyPI JSON API and AUR RPC API in `PyPIClient` and `AURClient`. These clients are instantiated in `DependencyResolver`, `PyPIGenerator`, and `Auditor`. Each invocation during a multi-package build produces redundant network requests for the same URLs.

The workspace already has a `srv/` directory for internal tool state. The cache will live alongside that state. The user has specified client-specific subdirectories (`network_cache/aur/`, `network_cache/pypi/`) that must never be wiped between runs.

## Goals / Non-Goals

**Goals:**
- Avoid redundant network requests to AUR and PyPI within a 1-hour window.
- Provide graceful fallback to stale cache data when network is unavailable.
- Cache only metadata JSON responses — never large binary artifacts like tarballs.
- Keep cache scoped to client (aur/pypi) for clarity and isolation.

**Non-Goals:**
- No cache eviction or size management beyond TTL staleness.
- No caching of `git clone` operations (AUR repos are already stored in `aur_packages/`).
- No user-facing CLI flags to control cache behavior in this change.
- No caching of requests within `updpkgsums` or chroot operations.

## Decisions

### Decision 1: File-based JSON cache, keyed by SHA-256 of URL

**Rationale:** Simple to implement, debuggable (JSON files are human-readable), and requires no additional dependencies. SHA-256 hashing avoids issues with URL-unsafe characters in filenames.

**Alternatives considered:**
- SQLite database: Overkill for key-value caching; adds dependency complexity.
- `requests-cache` library: Pulls in transitive dependencies; less control over storage layout and fallback behavior.

### Decision 2: 1-hour TTL with stale-on-failure

**Rationale:** AUR packages change infrequently; PyPI versions change infrequently. A 1-hour window prevents redundant calls during a build session while staying reasonably fresh. The "stale on failure" fallback ensures the tool remains functional when PyPI or AUR are temporarily unreachable or when the user is offline.

**Alternatives considered:**
- No TTL (always refresh): Defeats the purpose of caching.
- Cache-then-network race (stale-while-revalidate): Adds complexity for marginal benefit in a CLI tool.

### Decision 3: Atomic writes via tempfile

**Rationale:** Prevents cache corruption if the process is interrupted mid-write. Standard practice for file-based caches.

### Decision 4: 404 results cached as `null` data

**Rationale:** PyPI lookups for non-existent packages happen during the early stages of dependency resolution (PyPI tier). Caching a 404 prevents repeated failed lookups for the same missing package across multiple dependency sub-trees.

### Decision 5: Integration via dependency injection

**Rationale:** The `NetworkCache` instance is created in `Manager.__init__()` and passed to `DependencyResolver`, `PyPIGenerator`, and `AURClient`. This avoids global mutable state and makes testing straightforward.

## Risks / Trade-offs

- **Disk growth**: Over many sessions, cache directories accumulate files. Mitigation: TTL ensures stale files are overwritten on next success; 404 caches are small. Manual cleanup is possible but not required for normal operation.
- **Stale data**: If both AUR and PyPI are down for over an hour, the resolver will fall back to stale data which may produce incorrect dependency graphs. Mitigation: The warning log makes the user aware; this is better than failing entirely.
- **Cache key collision**: Extremely unlikely with SHA-256 of full URLs, but theoretically possible with URL parameter permutations producing different content at the same URL. Mitigation: The URLs we cache (PyPI `/json`, AUR `/rpc/v5/info`) are deterministic REST endpoints with no query parameter variations in our usage.

## Open Questions

- None at this time. The design is constrained by the user's explicit requirements.
