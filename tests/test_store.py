import asyncio

import pytest

from agbcia_web.store import ResultStore


@pytest.mark.asyncio
async def test_put_and_get_roundtrip():
    store = ResultStore(ttl_seconds=60, max_bytes=1_000_000)
    token, entry = await store.put(b"cia-bytes", "game.cia", {"title_id": "aa"})
    fetched = await store.get(token)
    assert fetched is entry
    assert fetched.data == b"cia-bytes"
    assert fetched.filename == "game.cia"


@pytest.mark.asyncio
async def test_get_returns_none_for_unknown_token():
    store = ResultStore(ttl_seconds=60, max_bytes=1_000_000)
    assert await store.get("nope") is None


@pytest.mark.asyncio
async def test_sweep_expired_removes_stale_entries():
    store = ResultStore(ttl_seconds=0, max_bytes=1_000_000)
    token, _entry = await store.put(b"data", "game.cia", {})
    await asyncio.sleep(0.01)
    removed = await store.sweep_expired()
    assert removed == 1
    assert await store.get(token) is None


@pytest.mark.asyncio
async def test_put_evicts_oldest_when_over_budget():
    store = ResultStore(ttl_seconds=60, max_bytes=10)
    first_token, _ = await store.put(b"1234567890", "a.cia", {})
    second_token, _ = await store.put(b"1234567890", "b.cia", {})
    assert await store.get(first_token) is None
    assert await store.get(second_token) is not None
