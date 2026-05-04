"""Tests for the NetworkCache class."""

import json
import os
import time
from unittest.mock import patch

import pytest
import requests

from aur_python_packer.cache import NetworkCache, CACHE_TTL


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def cache(tmp_path):
    """Return a NetworkCache rooted in a temporary directory."""
    yield NetworkCache(str(tmp_path))


def _cache_path(cache, url, client="pypi"):
    """Return the on-disk path for a given URL (convenience helper)."""
    return cache._cache_path(url, client)


def _write_cache(cache, url, data, client="pypi", age=0):
    """Write a cache entry with a given age (in seconds, 0 = fresh)."""
    entry = {
        "url": url,
        "timestamp": time.time() - age,
        "data": data,
    }
    path = _cache_path(cache, url, client)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(entry, f)


# ---------------------------------------------------------------------------
# Test: fresh cache hit (Task 7.1)
# ---------------------------------------------------------------------------

class TestFreshHit:
    def test_returns_data_when_fresh(self, cache):
        url = "https://pypi.org/pypi/requests/json"
        expected = {"name": "requests", "version": "2.31.0"}
        _write_cache(cache, url, expected, age=30)  # 30 seconds old

        result = cache.get(url, "pypi")
        assert result == expected

    def test_returns_none_when_missing(self, cache):
        result = cache.get("https://pypi.org/pypi/nonexistent/json", "pypi")
        assert result is None

    def test_returns_none_when_stale(self, cache):
        url = "https://pypi.org/pypi/requests/json"
        _write_cache(cache, url, {"name": "requests"}, age=CACHE_TTL + 60)

        result = cache.get(url, "pypi")
        assert result is None


# ---------------------------------------------------------------------------
# Test: stale cache with successful refresh (Task 7.2)
# ---------------------------------------------------------------------------

class TestStaleRefresh:
    def test_fetch_json_refreshes_stale(self, cache):
        url = "https://pypi.org/pypi/requests/json"
        old_data = {"name": "old"}
        fresh_data = {"info": {"name": "requests", "version": "2.32.0",
                                "summary": "New", "requires_dist": []}}
        _write_cache(cache, url, old_data, age=CACHE_TTL + 60)

        with patch("requests.get") as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = fresh_data

            result = cache.fetch_json(url, "pypi")

        assert result == fresh_data
        # Cache should now have the new data
        cached = cache.get(url, "pypi")
        assert cached == fresh_data


# ---------------------------------------------------------------------------
# Test: stale cache with network failure fallback (Task 7.3)
# ---------------------------------------------------------------------------

class TestStaleFallback:
    def test_uses_stale_when_network_fails(self, cache):
        url = "https://pypi.org/pypi/requests/json"
        stale_data = {"name": "requests", "version": "2.31.0"}
        _write_cache(cache, url, stale_data, age=CACHE_TTL + 60)

        with patch("requests.get") as mock_get:
            mock_get.side_effect = requests.ConnectionError("No network")

            result = cache.fetch_json(url, "pypi")

        assert result == stale_data

    def test_raises_when_no_cache_and_network_fails(self, cache):
        url = "https://pypi.org/pypi/unknown/json"

        with patch("requests.get") as mock_get:
            mock_get.side_effect = requests.ConnectionError("No network")

            with pytest.raises(RuntimeError, match="Failed to fetch"):
                cache.fetch_json(url, "pypi")


# ---------------------------------------------------------------------------
# Test: 404 caching (Task 7.4)
# ---------------------------------------------------------------------------

class Test404Caching:
    def test_returns_none_on_404(self, cache):
        url = "https://pypi.org/pypi/nonexistent/json"

        with patch("requests.get") as mock_get:
            mock_get.return_value.status_code = 404

            result = cache.fetch_json(url, "pypi")

        assert result is None

    def test_cached_404_served_without_network(self, cache):
        url = "https://pypi.org/pypi/nonexistent/json"

        # First request: cause a 404 (caches it)
        with patch("requests.get") as mock_get:
            mock_get.return_value.status_code = 404
            cache.fetch_json(url, "pypi")

        # Second request: should use cache, no network call
        with patch("requests.get") as mock_get:
            result = cache.fetch_json(url, "pypi")
            mock_get.assert_not_called()

        assert result is None


# ---------------------------------------------------------------------------
# Test: atomic write integrity (Task 7.5)
# ---------------------------------------------------------------------------

class TestAtomicWrite:
    def test_set_creates_valid_cache_entry(self, cache):
        url = "https://pypi.org/pypi/requests/json"
        data = {"name": "requests"}
        cache.set(url, "pypi", data)

        path = cache._cache_path(url, "pypi")
        assert os.path.exists(path)

        with open(path) as f:
            entry = json.load(f)
        assert entry["url"] == url
        assert entry["data"] == data
        assert "timestamp" in entry

    def test_multiple_clients_separate_dirs(self, cache):
        url = "https://pypi.org/pypi/requests/json"
        cache.set(url, "pypi", {"source": "pypi"})
        cache.set(url, "aur", {"source": "aur"})

        pypi_path = cache._cache_path(url, "pypi")
        aur_path = cache._cache_path(url, "aur")
        assert pypi_path != aur_path
        assert os.path.exists(pypi_path)
        assert os.path.exists(aur_path)


# ---------------------------------------------------------------------------
# Test: client integration (Tasks 7.6, 7.7)
# ---------------------------------------------------------------------------

class TestClientIntegration:
    def test_pypi_client_uses_cache(self, cache):
        from aur_python_packer.clients import PyPIClient

        client = PyPIClient(cache=cache)
        url = "https://pypi.org/pypi/requests/json"
        fresh_data = {
            "info": {
                "name": "requests",
                "version": "2.31.0",
                "summary": "S",
                "license": "MIT",
                "classifiers": [],
                "requires_dist": [],
            },
            "urls": [],
        }

        # Pre-populate cache
        _write_cache(cache, url, fresh_data, age=30)

        meta = client.get_metadata("requests")
        assert meta["name"] == "requests"
        assert meta["version"] == "2.31.0"

    def test_aur_client_uses_cache(self, cache):
        from aur_python_packer.clients import AURClient

        client = AURClient(cache=cache)
        url = "https://aur.archlinux.org/rpc/v5/info?arg[]=python-requests"
        fresh_data = {
            "resultcount": 1,
            "results": [{"Name": "python-requests", "Version": "2.31.0"}],
        }

        _write_cache(cache, url, fresh_data, client="aur", age=30)

        info = client.get_info("python-requests")
        assert info is not None
        assert info["Name"] == "python-requests"

    def test_pypi_client_no_cache_falls_back(self):
        """Without a cache, PyPIClient should still work (direct HTTP)."""
        from aur_python_packer.clients import PyPIClient

        client = PyPIClient(cache=None)

        with patch("requests.get") as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {
                "info": {
                    "name": "requests",
                    "version": "2.31.0",
                    "summary": "S",
                    "license": "MIT",
                    "classifiers": [],
                    "requires_dist": [],
                },
                "urls": [],
            }

            meta = client.get_metadata("requests")
            assert meta["version"] == "2.31.0"
