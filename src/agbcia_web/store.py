"""In-memory store for generated CIA results, keyed by a random token.

Entries expire after a fixed TTL from creation; a background sweep
(``run_cleanup_loop``) removes expired entries on an interval. A byte
budget evicts the oldest entries first when exceeded, independent of TTL.
"""

from __future__ import annotations

import asyncio
import secrets
import time
from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class StoredResult:
    data: bytes
    filename: str
    metadata: dict[str, str]
    expires_at: float


@dataclass(slots=True)
class ResultStore:
    ttl_seconds: int
    max_bytes: int
    _entries: dict[str, StoredResult] = field(default_factory=dict)
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock)

    async def put(
        self, data: bytes, filename: str, metadata: dict[str, str]
    ) -> tuple[str, StoredResult]:
        token = secrets.token_urlsafe(16)
        entry = StoredResult(
            data=data,
            filename=filename,
            metadata=metadata,
            expires_at=time.monotonic() + self.ttl_seconds,
        )
        async with self._lock:
            self._entries[token] = entry
            self._evict_over_budget()
        return token, entry

    async def get(self, token: str) -> StoredResult | None:
        async with self._lock:
            return self._entries.get(token)

    async def sweep_expired(self) -> int:
        now = time.monotonic()
        async with self._lock:
            expired = [token for token, entry in self._entries.items() if entry.expires_at <= now]
            for token in expired:
                del self._entries[token]
            return len(expired)

    def _evict_over_budget(self) -> None:
        total = sum(len(entry.data) for entry in self._entries.values())
        if total <= self.max_bytes:
            return
        oldest_first = sorted(self._entries.items(), key=lambda item: item[1].expires_at)
        for token, entry in oldest_first:
            if total <= self.max_bytes:
                break
            del self._entries[token]
            total -= len(entry.data)


async def run_cleanup_loop(store: ResultStore, interval_seconds: int) -> None:
    while True:
        await asyncio.sleep(interval_seconds)
        await store.sweep_expired()
