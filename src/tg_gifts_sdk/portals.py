"""Portals marketplace client — interface stub.

Status: scaffolded; not implemented yet.

Endpoint hints (community-reported, NOT verified by this SDK):
  Base URL: https://portals-market.com/api (subject to change)
  Auth: Telegram WebApp initData via `Authorization: tma <initData>` header
  Listings: GET /nfts/search or POST /v2/nfts/list (versioning unclear)

If you want to contribute a working implementation, see CONTRIBUTING.md.
The unified `Listing` model in `tg_gifts_sdk.models` is the target shape.
"""
from __future__ import annotations

from types import TracebackType

from tg_gifts_sdk.exceptions import NotImplementedYetError
from tg_gifts_sdk.models import FloorStats, Listing


class PortalsClient:
    """Async client stub for the Portals marketplace.

    All methods raise `NotImplementedYetError` with implementation hints.
    The class exists so `UnifiedClient` can be instantiated against the
    full multi-venue surface even when only Tonnel is wired up.
    """

    def __init__(self, *, auth_data: str = "", timeout: float = 30.0) -> None:
        self.auth_data = auth_data
        self.timeout = timeout

    async def __aenter__(self) -> PortalsClient:
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

    async def fetch_listings(self, **kwargs: object) -> list[Listing]:
        raise NotImplementedYetError(
            marketplace="portals",
            operation="fetch_listings",
            hint="Portals API not yet reverse-engineered. Contributions welcome — "
                 "see CONTRIBUTING.md. Suggested entry point: capture cURL from "
                 "https://portals-market.com network tab, share in a GH issue.",
        )

    async def fetch_floor_stats(self) -> list[FloorStats]:
        raise NotImplementedYetError(
            marketplace="portals",
            operation="fetch_floor_stats",
            hint="Portals API not yet reverse-engineered.",
        )
