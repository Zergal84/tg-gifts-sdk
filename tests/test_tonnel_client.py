"""Unit tests for TonnelClient — uses monkeypatched _http.post_json (no network)."""
from __future__ import annotations

from typing import Any

import pytest

from tg_gifts_sdk import (
    AuthDataMissingError,
    FloorStats,
    Listing,
    MarketplaceUnavailableError,
)
from tg_gifts_sdk.tonnel import TonnelClient


@pytest.fixture
def auth_data() -> str:
    return "user=...&hash=...&signature=..."


@pytest.fixture
def mock_post(monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    """Replace _http.post_json with a controllable mock. Returns the call log."""
    from tg_gifts_sdk import tonnel as tonnel_mod

    calls: list[dict[str, Any]] = []
    responses: list[tuple[int, Any]] = []

    async def fake_post(
        url: str, *, json_body: dict[str, Any], headers: dict[str, str],
        impersonate: str = "firefox133", timeout: float = 30.0,
    ) -> tuple[int, Any]:
        calls.append({"url": url, "json": json_body, "headers": headers})
        if responses:
            return responses.pop(0)
        return (200, {})

    monkeypatch.setattr(tonnel_mod, "post_json", fake_post)
    return {"calls": calls, "responses": responses}


@pytest.mark.asyncio
async def test_fetch_listings_parses_response(auth_data: str, mock_post: dict) -> None:
    mock_post["responses"].append((200, [
        {
            "gift_id": 12345, "gift_name": "Plush Pepe", "gift_num": 42,
            "model": "Diamond (5%)", "backdrop": "Pink (10%)", "symbol": "Crown (3%)",
            "price": 800.0, "asset": "TON", "seller": "UQABC",
        },
        {
            "gift_id": 67890, "gift_name": "Plush Pepe", "gift_num": 100,
            "model": None, "backdrop": None, "symbol": None,
            "price": 200.0, "asset": "TON", "seller": "UQDEF",
        },
    ]))

    async with TonnelClient(auth_data=auth_data) as client:
        listings = await client.fetch_listings(gift_name="Plush Pepe", limit=10)

    assert len(listings) == 2
    assert all(isinstance(l, Listing) for l in listings)
    assert listings[0].marketplace == "tonnel"
    assert listings[0].gift_id == 12345
    assert listings[0].price == 800.0
    assert listings[0].model == "Diamond (5%)"
    assert listings[1].model is None

    call = mock_post["calls"][0]
    assert call["url"].endswith("/api/pageGifts")
    assert call["json"]["limit"] == 10
    assert call["json"]["user_auth"] == auth_data


@pytest.mark.asyncio
async def test_fetch_listings_drops_malformed_items(auth_data: str, mock_post: dict) -> None:
    mock_post["responses"].append((200, [
        {"gift_id": 1, "gift_name": "X", "gift_num": 1, "price": 10.0, "asset": "TON"},
        "not_a_dict",
        None,
        {"gift_id": 2, "gift_name": "Y", "gift_num": 2, "price": 20.0, "asset": "TON"},
    ]))

    async with TonnelClient(auth_data=auth_data) as client:
        listings = await client.fetch_listings(limit=10)

    assert len(listings) == 2
    assert [l.gift_id for l in listings] == [1, 2]


@pytest.mark.asyncio
async def test_fetch_listings_wraps_envelope(auth_data: str, mock_post: dict) -> None:
    """Tonnel sometimes returns {gifts: [...]} or {data: [...]} instead of bare list."""
    mock_post["responses"].append((200, {
        "gifts": [
            {"gift_id": 1, "gift_name": "X", "gift_num": 1, "price": 10.0, "asset": "TON"},
        ],
    }))

    async with TonnelClient(auth_data=auth_data) as client:
        listings = await client.fetch_listings()

    assert len(listings) == 1


@pytest.mark.asyncio
async def test_fetch_listings_raises_on_http_error(auth_data: str, mock_post: dict) -> None:
    mock_post["responses"].append((403, "blocked by CloudFlare"))

    async with TonnelClient(auth_data=auth_data) as client:
        with pytest.raises(MarketplaceUnavailableError) as exc_info:
            await client.fetch_listings()

    assert exc_info.value.marketplace == "tonnel"
    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_fetch_listings_requires_auth(mock_post: dict) -> None:
    with pytest.raises(AuthDataMissingError):
        async with TonnelClient(auth_data="") as client:
            await client.fetch_listings()


@pytest.mark.asyncio
async def test_fetch_floor_stats_parses_envelope(auth_data: str, mock_post: dict) -> None:
    mock_post["responses"].append((200, {
        "status": "success",
        "data": {
            "Plush Pepe": {
                "floor": 800,
                "models": {"Diamond": 5000, "Gold": 3000},
                "backdrops": {"Pink": 6000},
                "symbols": {},
            },
            "Crystal Ball": {
                "floor": 200,
                "models": {"Common": 200},
                "backdrops": {},
                "symbols": {},
            },
        },
    }))

    async with TonnelClient(auth_data=auth_data) as client:
        stats = await client.fetch_floor_stats()

    assert len(stats) == 2
    pp = next(s for s in stats if s.collection == "Plush Pepe")
    assert isinstance(pp, FloorStats)
    assert pp.marketplace == "tonnel"
    assert pp.floor == 800.0
    assert pp.models["Diamond"] == 5000.0


@pytest.mark.asyncio
async def test_fetch_balance_parses_response(auth_data: str, mock_post: dict) -> None:
    mock_post["responses"].append((200, {
        "balance": 42.5,
        "usdtBalance": 12.0,
        "tonnelBalance": 0,
        "memo": "abcdef",
        "name": "operator",
    }))

    async with TonnelClient(auth_data=auth_data) as client:
        info = await client.fetch_balance()

    assert info.balance_ton == 42.5
    assert info.balance_usdt == 12.0
    assert info.memo == "abcdef"
    assert info.name == "operator"


@pytest.mark.asyncio
async def test_fetch_balance_handles_missing_fields(auth_data: str, mock_post: dict) -> None:
    mock_post["responses"].append((200, {}))

    async with TonnelClient(auth_data=auth_data) as client:
        info = await client.fetch_balance()

    assert info.balance_ton == 0.0
    assert info.balance_usdt == 0.0
    assert info.memo == ""


@pytest.mark.asyncio
async def test_client_context_manager_is_required(auth_data: str) -> None:
    client = TonnelClient(auth_data=auth_data)
    assert client.auth_data == auth_data
    await client.aclose()
