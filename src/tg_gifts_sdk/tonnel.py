"""Tonnel marketplace client — async, read-only.

Reverse-engineered against Tonnel's `gifts2.tonnel.network` API with the
`marketplace.tonnel.network` origin headers. Uses curl_cffi Firefox 133
impersonation to satisfy CloudFlare TLS fingerprinting.

Read-only scope:
- Listings (pageGifts)
- Floor stats per collection (filterStats)
- Account balance + memo (balance/info)

Write operations (buyGift, listGift, etc.) are NOT included in this SDK to
keep the public surface conservative; the marketplace's signing protocol
(`wtf` field) is left to downstream users to reverse-engineer themselves.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from types import TracebackType
from typing import Any

from tg_gifts_sdk._http import build_firefox_headers, post_json
from tg_gifts_sdk.exceptions import (
    AuthDataMissingError,
    MarketplaceUnavailableError,
)
from tg_gifts_sdk.models import FloorStats, Listing

TONNEL_API_BASE = "https://gifts2.tonnel.network/api"
TONNEL_ORIGIN = "https://marketplace.tonnel.network"
TONNEL_HOST = "gifts2.tonnel.network"

SORTS: dict[str, str] = {
    "price_asc": '{"price":1,"gift_id":-1}',
    "price_desc": '{"price":-1,"gift_id":-1}',
    "latest": '{"message_post_time":-1,"gift_id":-1}',
    "mint_time": '{"export_at":1,"gift_id":-1}',
    "rarity": '{"rarity":-1,"gift_id":-1}',
    "gift_id_asc": '{"gift_num":1,"gift_id":-1}',
    "gift_id_desc": '{"gift_num":-1,"gift_id":-1}',
}


@dataclass(frozen=True)
class BalanceInfo:
    """Operator's balance + identifying metadata from Tonnel."""

    balance_ton: float
    balance_usdt: float
    balance_tonnel: float
    memo: str
    name: str


def _tonnel_title(text: str) -> str:
    """Title-case fragments matching how Tonnel stores collection/model names."""
    return " ".join(
        (word[:1].upper() + word[1:]) if word else "" for word in text.split()
    )


def _parse_listing(item: dict[str, Any]) -> Listing | None:
    """Convert one raw Tonnel listing dict → typed Listing. None on malformed input."""
    try:
        return Listing(
            marketplace="tonnel",
            gift_id=int(item.get("gift_id") or item.get("_id") or 0),
            gift_name=str(
                item.get("gift_name")
                or item.get("name")
                or item.get("collection_name")
                or ""
            ),
            gift_num=int(item.get("gift_num") or item.get("num") or 0),
            model=item.get("model"),
            backdrop=item.get("backdrop"),
            symbol=item.get("symbol"),
            price=float(item.get("price") or 0),
            asset=str(item.get("asset") or "TON"),  # type: ignore[arg-type]
            seller=item.get("seller") or item.get("owner"),
            raw=item,
        )
    except (ValueError, TypeError):
        return None


class TonnelClient:
    """Async read-only client for the Tonnel marketplace.

    Usage:
        async with TonnelClient(auth_data="user=...") as client:
            listings = await client.fetch_listings(gift_name="Plush Pepe")
            stats = await client.fetch_floor_stats()
            info = await client.fetch_balance()

    `auth_data` is the URL-encoded Telegram WebApp `initData` string captured
    from `localStorage.getItem("web-initData")` while logged into
    https://marketplace.tonnel.network. It expires every 24-72 hours; refresh
    by re-extracting from the browser.
    """

    def __init__(
        self,
        *,
        auth_data: str,
        timeout: float = 30.0,
    ) -> None:
        self.auth_data = auth_data
        self.timeout = timeout

    async def __aenter__(self) -> TonnelClient:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        return None

    async def fetch_listings(
        self,
        *,
        gift_name: str | None = None,
        model: str | None = None,
        backdrop: str | None = None,
        symbol: str | None = None,
        sort: str = "price_asc",
        limit: int = 30,
        page: int = 1,
        asset: str = "TON",
    ) -> list[Listing]:
        self._require_auth()
        if sort not in SORTS:
            raise ValueError(f"sort must be one of {sorted(SORTS)}")

        filter_dict: dict[str, Any] = {
            "price": {"$exists": True},
            "buyer": {"$exists": False},
            "asset": asset,
            "refunded": {"$ne": True},
            "export_at": {"$exists": True},
        }
        if gift_name:
            filter_dict["gift_name"] = _tonnel_title(gift_name.strip())
        for key, value in (("model", model), ("backdrop", backdrop), ("symbol", symbol)):
            if value:
                if "(" in value:
                    filter_dict[key] = _tonnel_title(value.strip())
                else:
                    filter_dict[key] = {"$regex": f"^{_tonnel_title(value.strip())} \\("}

        payload = {
            "filter": json.dumps(filter_dict),
            "limit": limit,
            "page": page,
            "sort": SORTS[sort],
            "ref": 0,
            "price_range": 0,
            "user_auth": self.auth_data,
        }

        status, body = await post_json(
            f"{TONNEL_API_BASE}/pageGifts",
            json_body=payload,
            headers=build_firefox_headers(origin=TONNEL_ORIGIN, host=TONNEL_HOST),
            timeout=self.timeout,
        )

        if status != 200:
            raise MarketplaceUnavailableError(
                marketplace="tonnel",
                status_code=status,
                body=str(body),
            )

        if isinstance(body, list):
            items = body
        elif isinstance(body, dict):
            items = body.get("gifts") or body.get("data") or []
        else:
            items = []

        listings: list[Listing] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            parsed = _parse_listing(item)
            if parsed is not None:
                listings.append(parsed)
        return listings

    async def fetch_floor_stats(self) -> list[FloorStats]:
        self._require_auth()
        status, body = await post_json(
            f"{TONNEL_API_BASE}/filterStats",
            json_body={"authData": self.auth_data},
            headers=build_firefox_headers(origin=TONNEL_ORIGIN, host=TONNEL_HOST),
            timeout=self.timeout,
        )

        if status != 200:
            raise MarketplaceUnavailableError(
                marketplace="tonnel",
                status_code=status,
                body=str(body),
            )

        if isinstance(body, dict) and body.get("status") == "success" and "data" in body:
            data = body["data"]
        else:
            data = body

        if not isinstance(data, dict):
            return []

        stats: list[FloorStats] = []
        for collection_name, payload in data.items():
            if not isinstance(payload, dict):
                continue
            try:
                stats.append(FloorStats(
                    marketplace="tonnel",
                    collection=str(collection_name),
                    floor=float(payload.get("floor") or 0),
                    models={
                        str(k): float(v) for k, v in (payload.get("models") or {}).items()
                        if isinstance(v, (int, float))
                    },
                    backdrops={
                        str(k): float(v) for k, v in (payload.get("backdrops") or {}).items()
                        if isinstance(v, (int, float))
                    },
                    symbols={
                        str(k): float(v) for k, v in (payload.get("symbols") or {}).items()
                        if isinstance(v, (int, float))
                    },
                ))
            except (ValueError, TypeError):
                continue
        return stats

    async def fetch_balance(self) -> BalanceInfo:
        self._require_auth()
        status, body = await post_json(
            f"{TONNEL_API_BASE}/balance/info",
            json_body={"authData": self.auth_data},
            headers=build_firefox_headers(origin=TONNEL_ORIGIN, host=TONNEL_HOST),
            timeout=self.timeout,
        )

        if status != 200:
            raise MarketplaceUnavailableError(
                marketplace="tonnel",
                status_code=status,
                body=str(body),
            )

        if not isinstance(body, dict):
            body = {}

        return BalanceInfo(
            balance_ton=float(body.get("balance") or 0),
            balance_usdt=float(body.get("usdtBalance") or 0),
            balance_tonnel=float(body.get("tonnelBalance") or 0),
            memo=str(body.get("memo") or ""),
            name=str(body.get("name") or ""),
        )

    def _require_auth(self) -> None:
        if not self.auth_data:
            raise AuthDataMissingError(
                "TonnelClient requires auth_data — see README for how to capture "
                "initData from marketplace.tonnel.network localStorage."
            )
