"""Fragment stub tests — verify exceptions and surface shape."""
from __future__ import annotations

import pytest

from tg_gifts_sdk import NotImplementedYetError
from tg_gifts_sdk.fragment import FragmentClient


@pytest.mark.asyncio
async def test_fragment_listings_raises_not_implemented() -> None:
    async with FragmentClient() as client:
        with pytest.raises(NotImplementedYetError) as exc:
            await client.fetch_listings()
    assert exc.value.marketplace == "fragment"


@pytest.mark.asyncio
async def test_fragment_floor_stats_raises_not_implemented() -> None:
    async with FragmentClient() as client:
        with pytest.raises(NotImplementedYetError):
            await client.fetch_floor_stats()
