import hashlib
import json
import logging
import os
import tempfile
import time

import requests

logger = logging.getLogger(__name__)

# Cache entries older than this (in seconds) are considered stale.
CACHE_TTL = 3600  # 1 hour


class NetworkCache:
    """
    File-based JSON cache for network API responses.

    Stores cached responses in client-specific subdirectories under
    <base_dir>/srv/network_cache/<client>/.  Each cached URL is keyed by
    the SHA-256 digest of its URL string.

    Provides a fetch_json() convenience that handles the full lifecycle:
      - return fresh cache
      - refresh stale cache on network success
      - fall back to stale cache on network failure
      - cache 404 responses as ``null`` data
    """

    def __init__(self, base_dir):
        self.base_dir = os.path.abspath(base_dir)
        self._cache_root = os.path.join(self.base_dir, "srv", "network_cache")

    def _client_dir(self, client):
        """Return the cache directory for *client*, creating it if needed."""
        d = os.path.join(self._cache_root, client)
        os.makedirs(d, exist_ok=True)
        return d

    def _cache_path(self, url, client):
        """Return the filesystem path for the cache entry of *url* under *client*."""
        digest = hashlib.sha256(url.encode("utf-8")).hexdigest()
        return os.path.join(self._client_dir(client), digest)

    # ------------------------------------------------------------------
    # Low-level helpers
    # ------------------------------------------------------------------

    def get(self, url, client):
        """
        Return the cached data for *url* under *client*, or ``None`` if
        the cache entry is missing or stale.
        """
        path = self._cache_path(url, client)
        try:
            with open(path, "r") as f:
                entry = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return None

        age = time.time() - entry["timestamp"]
        if age > CACHE_TTL:
            logger.debug("Cache entry stale for %s (%.0f seconds old)", url, age)
            return None

        logger.debug("Cache hit for %s", url)
        return entry["data"]

    def set(self, url, client, data):
        """
        Persist *data* for *url* under *client*.

        Writes are performed atomically by writing to a temporary file
        in the same directory and then renaming it into place.
        """
        path = self._cache_path(url, client)
        entry = {"url": url, "timestamp": time.time(), "data": data}
        fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path))
        try:
            with os.fdopen(fd, "w") as f:
                json.dump(entry, f)
            os.replace(tmp, path)
        except Exception:
            # Clean up the temp file on failure
            try:
                os.unlink(tmp)
            except OSError:
                pass
            raise

    # ------------------------------------------------------------------
    # High-level API
    # ------------------------------------------------------------------

    def fetch_json(self, url, client, timeout=10):
        """
        Retrieve JSON data from *url*, using the cache under *client*.

        The cache is first consulted.  If the cached entry is fresh it is
        returned immediately.  If stale, an attempt is made to refresh from
        the network.

        **Stale fallback**: if the network request fails and a stale cache
        entry exists, a warning is logged and the stale data is returned.

        **No-cache fallback**: if no cache entry exists and the network
        request fails, the underlying exception is re-raised.

        **404 caching**: when the server returns a 404, the result is
        cached as ``None`` so that repeated lookups are short-circuited.
        """
        # 1. Check cache
        cached, is_not_found = self._get_with_not_found_flag(url, client)

        # 2. If fresh, return immediately
        if cached is not None or is_not_found:
            return cached

        # 3. Attempt network refresh
        try:
            resp = requests.get(url, timeout=timeout)
            if resp.status_code == 200:
                data = resp.json()
                self.set(url, client, data)
                return data

            # 404: cache as not-found marker
            if resp.status_code == 404:
                self.set(url, client, None)
                return None

            resp.raise_for_status()
        except requests.RequestException as e:
            logger.warning("Network request failed for %s: %s", url, e)

        # 4. Fallback to stale cache
        stale, stale_is_not_found = self._get_stale_with_flag(url, client)
        if stale is not None or stale_is_not_found:
            if stale_is_not_found:
                logger.warning(
                    "Using stale cached 404 for %s (network unavailable)", url
                )
            else:
                logger.warning(
                    "Using stale cached data for %s (network unavailable)", url
                )
            return stale

        raise RuntimeError(f"Failed to fetch {url} and no cached data available")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_stale(self, url, client):
        """
        Return the cached data for *url* regardless of age, or ``None``
        if no cache entry exists.
        """
        path = self._cache_path(url, client)
        try:
            with open(path, "r") as f:
                entry = json.load(f)
            return entry["data"]
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            return None

    def _get_with_not_found_flag(self, url, client):
        """
        Return a ``(data, is_not_found)`` tuple.

        ``is_not_found`` is ``True`` when the cache entry is a fresh
        cached 404 response (data stored as None).
        """
        path = self._cache_path(url, client)
        try:
            with open(path, "r") as f:
                entry = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return None, False

        age = time.time() - entry["timestamp"]
        if age > CACHE_TTL:
            logger.debug("Cache entry stale for %s (%.0f seconds old)", url, age)
            return None, False

        logger.debug("Cache hit for %s", url)
        data = entry["data"]
        # A cached 404 is stored as ``null`` (None) in JSON.
        # We distinguish "not found" from "no entry" via the tuple return path.
        if data is not None:
            return data, False
        return None, True

    def _get_stale_with_flag(self, url, client):
        """
        Like :meth:`_get_with_not_found_flag` but ignores TTL.
        """
        path = self._cache_path(url, client)
        try:
            with open(path, "r") as f:
                entry = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return None, False
        data = entry.get("data")
        if data is not None:
            return data, False
        return None, True
