"""Live integration smoke — skipped unless TONNEL_AUTH_DATA env is set.

Run locally (Windows PowerShell):
    $env:TONNEL_AUTH_DATA = "user=...&hash=..."
    pytest tests/test_smoke.py -v -m integration
"""
from __future__ import annotations

import pytest

from tg_gifts_sdk import TonnelClient

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_smoke_fetch_balance_succeeds(tonnel_auth_data_or_skip: str) -> None:
    async with TonnelClient(auth_data=tonnel_auth_data_or_skip) as client:
        info = await client.fetch_balance()
    assert info.memo
    assert info.balance_ton >= 0


@pytest.mark.asyncio
async def test_smoke_fetch_floor_stats_returns_collections(tonnel_auth_data_or_skip: str) -> None:
    async with TonnelClient(auth_data=tonnel_auth_data_or_skip) as client:
        stats = await client.fetch_floor_stats()
    assert len(stats) >= 1
    assert all(s.collection for s in stats)


@pytest.mark.asyncio
async def test_smoke_fetch_listings_returns_listings(tonnel_auth_data_or_skip: str) -> None:
    async with TonnelClient(auth_data=tonnel_auth_data_or_skip) as client:
        listings = await client.fetch_listings(limit=5)
    assert len(listings) >= 1
    assert all(item.marketplace == "tonnel" for item in listings)
    assert all(item.price >= 0 for item in listings)
