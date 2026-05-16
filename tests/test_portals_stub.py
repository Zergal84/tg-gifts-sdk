"""Portals stub tests — verify exceptions and surface shape."""
from __future__ import annotations

import pytest

from tg_gifts_sdk import NotImplementedYetError
from tg_gifts_sdk.portals import PortalsClient


@pytest.mark.asyncio
async def test_portals_listings_raises_not_implemented() -> None:
    async with PortalsClient() as client:
        with pytest.raises(NotImplementedYetError) as exc:
            await client.fetch_listings()
    assert exc.value.marketplace == "portals"
    assert exc.value.operation == "fetch_listings"
    assert exc.value.hint


@pytest.mark.asyncio
async def test_portals_floor_stats_raises_not_implemented() -> None:
    async with PortalsClient() as client:
        with pytest.raises(NotImplementedYetError):
            await client.fetch_floor_stats()


@pytest.mark.asyncio
async def test_portals_close_is_noop() -> None:
    client = PortalsClient()
    await client.aclose()
    await client.aclose()
