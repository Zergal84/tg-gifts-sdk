"""UnifiedClient tests — verify Tonnel-backed aggregation, graceful stub handling."""
from __future__ import annotations

from typing import Any

import pytest

from tg_gifts_sdk.unified import UnifiedClient


@pytest.fixture
def auth_data() -> str:
    return "user=...&hash=..."


@pytest.fixture
def mock_post(monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    from tg_gifts_sdk import tonnel as tonnel_mod
    calls: list[dict[str, Any]] = []
    responses: list[tuple[int, Any]] = []

    async def fake_post(
        url: str, *, json_body: dict[str, Any], headers: dict[str, str],
        impersonate: str = "firefox133",
        timeout: float = 30.0,  # noqa: ASYNC109 — mirrors sync curl_cffi timeout
    ) -> tuple[int, Any]:
        calls.append({"url": url, "json": json_body})
        if responses:
            return responses.pop(0)
        return (200, [])

    monkeypatch.setattr(tonnel_mod, "post_json", fake_post)
    return {"calls": calls, "responses": responses}


@pytest.mark.asyncio
async def test_unified_listings_calls_only_implemented_clients(auth_data: str, mock_post: dict[str, Any]) -> None:
    """Default `venues=None` skips stubbed Portals/Fragment, returns Tonnel results."""
    mock_post["responses"].append((200, [
        {"gift_id": 1, "gift_name": "X", "gift_num": 1, "price": 10.0, "asset": "TON"},
    ]))

    async with UnifiedClient(tonnel_auth=auth_data) as client:
        listings = await client.fetch_listings(gift_name="X")

    assert len(listings) == 1
    assert listings[0].marketplace == "tonnel"


@pytest.mark.asyncio
async def test_unified_can_target_single_venue(auth_data: str, mock_post: dict[str, Any]) -> None:
    mock_post["responses"].append((200, [
        {"gift_id": 1, "gift_name": "X", "gift_num": 1, "price": 10.0, "asset": "TON"},
    ]))

    async with UnifiedClient(tonnel_auth=auth_data) as client:
        listings = await client.fetch_listings(venues=["tonnel"])

    assert all(item.marketplace == "tonnel" for item in listings)


@pytest.mark.asyncio
async def test_unified_explicit_stub_venue_returns_empty(auth_data: str, mock_post: dict[str, Any]) -> None:
    async with UnifiedClient(tonnel_auth=auth_data) as client:
        listings = await client.fetch_listings(venues=["portals"])

    assert listings == []


@pytest.mark.asyncio
async def test_unified_raise_on_unimplemented_when_requested(auth_data: str, mock_post: dict[str, Any]) -> None:
    from tg_gifts_sdk import NotImplementedYetError

    async with UnifiedClient(tonnel_auth=auth_data) as client:
        with pytest.raises(NotImplementedYetError):
            await client.fetch_listings(
                venues=["portals"],
                raise_on_unimplemented=True,
            )


@pytest.mark.asyncio
async def test_unified_floor_stats_tonnel_only(auth_data: str, mock_post: dict[str, Any]) -> None:
    mock_post["responses"].append((200, {
        "status": "success",
        "data": {"X": {"floor": 100, "models": {}, "backdrops": {}, "symbols": {}}},
    }))

    async with UnifiedClient(tonnel_auth=auth_data) as client:
        stats = await client.fetch_floor_stats()

    assert len(stats) == 1
    assert stats[0].marketplace == "tonnel"
    assert stats[0].collection == "X"


@pytest.mark.asyncio
async def test_unified_returns_partial_on_one_venue_failure(auth_data: str, mock_post: dict[str, Any]) -> None:
    mock_post["responses"].append((200, [
        {"gift_id": 1, "gift_name": "X", "gift_num": 1, "price": 10.0, "asset": "TON"},
    ]))

    async with UnifiedClient(tonnel_auth=auth_data) as client:
        listings = await client.fetch_listings(venues=["tonnel", "portals"])

    assert len(listings) == 1
    assert listings[0].marketplace == "tonnel"
