## 1. Core Caching Implementation

- [x] 1.1 Create `aur_python_packer/cache.py` with `NetworkCache` class
- [x] 1.2 Implement `__init__(self, base_dir)` creating `srv/network_cache/<client>/` dirs
- [x] 1.3 Implement `_cache_path(url, client)` returning SHA-256 hashed path
- [x] 1.4 Implement `get(url, client)` returning cached data or None if stale/missing
- [x] 1.5 Implement `set(url, client, data)` writing JSON with atomic tempfile rename
- [x] 1.6 Implement `fetch_json(url, client, timeout)` with TTL, stale fallback, 404 caching
- [x] 1.7 Use `time.time()` for timestamp comparison in TTL checks

## 2. Client Integration

- [x] 2.1 Add optional `cache=None` parameter to `PyPIClient.__init__`
- [x] 2.2 Update `PyPIClient.get_metadata` to use `self.cache.fetch_json(url, "pypi")`
- [x] 2.3 Update `PyPIClient.get_release_info` to use `self.cache.fetch_json(url, "pypi")`
- [x] 2.4 Update `PyPIClient.verify_existence` to use `self.cache.fetch_json(url, "pypi")`
- [x] 2.5 Add optional `cache=None` parameter to `AURClient.__init__`
- [x] 2.6 Update `AURClient.get_info` to use `self.cache.fetch_json(url, "aur")`

## 3. Manager Orchestration

- [x] 3.1 Add `self.cache` initialization in `Manager.__init__` using `srv/network_cache/`
- [x] 3.2 Pass `self.cache` to `DependencyResolver`
- [x] 3.3 Pass `self.cache` to `PyPIGenerator`
- [x] 3.4 Pass `self.cache` to `AURClient`

## 4. Resolver Wiring

- [x] 4.1 Accept `cache` parameter in `DependencyResolver.__init__`
- [x] 4.2 Pass `cache` to internal `PyPIClient` and `AURClient` instances
- [x] 4.3 Update `resolver.py` imports to reference `NetworkCache` via type hint

## 5. Generator Wiring

- [x] 5.1 Accept `cache` parameter in `PyPIGenerator.__init__`
- [x] 5.2 Pass `cache` to internal `PyPIClient` instance

## 6. Auditor Wiring

- [x] 6.1 Accept `cache` parameter in `Auditor.__init__`
- [x] 6.2 Pass `cache` to internal `PyPIClient` instance
- [x] 6.3 Update `Manager.build_all` (or audit call site) to pass cache to Auditor

## 7. Tests

- [x] 7.1 Test `NetworkCache` fresh hit (under 1 hour)
- [x] 7.2 Test `NetworkCache` stale cache with successful refresh
- [x] 7.3 Test `NetworkCache` stale cache with network failure fallback
- [x] 7.4 Test `NetworkCache` 404 caching
- [x] 7.5 Test `NetworkCache` atomic write integrity
- [x] 7.6 Test client integration: PyPIClient uses cache when available
- [x] 7.7 Test client integration: AURClient uses cache when available
