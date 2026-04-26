from __future__ import annotations

import threading
import time
from typing import Any, Optional


class TTLCache:
    """Thread-safe in-memory cache with per-entry time-to-live expiry."""

    def __init__(self, ttl_seconds: int = 300) -> None:
        self._ttl = ttl_seconds
        self._store: dict[str, tuple[Any, float]] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[Any]:
        """Return the cached value for *key*, or None if missing / expired."""
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            value, expiry = entry
            if time.monotonic() > expiry:
                del self._store[key]
                return None
            return value

    def set(self, key: str, value: Any) -> None:
        """Store *value* under *key* with the configured TTL."""
        expiry = time.monotonic() + self._ttl
        with self._lock:
            self._store[key] = (value, expiry)

    def invalidate(self, key: str) -> None:
        """Remove a single entry from the cache."""
        with self._lock:
            self._store.pop(key, None)

    def clear(self) -> None:
        """Remove all entries from the cache."""
        with self._lock:
            self._store.clear()
