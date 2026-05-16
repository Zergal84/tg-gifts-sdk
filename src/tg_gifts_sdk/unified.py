"""UnifiedClient — single async surface aggregating across all marketplace clients.

Current behaviour:
- Tonnel: fully functional (delegates to TonnelClient).
- Portals + Fragment: stubs. By default, `UnifiedClient` silently skips them
  and returns only what implemented venues produce. Set
  `raise_on_unimplemented=True` per call to fail loudly instead.

Future behaviour (when stubs are filled in): same surface, no caller changes.
"""
from __future__ import annotations

from types import TracebackType
from typing import Any

from tg_gifts_sdk.exceptions import NotImplementedYetError
from tg_gifts_sdk.fragment import FragmentClient
from tg_gifts_sdk.models import FloorStats, Listing, Marketplace
from tg_gifts_sdk.portals import PortalsClient
from tg_gifts_sdk.tonnel import TonnelClient


class UnifiedClient:
    """Aggregating async client for all supported marketplaces.

    Usage:
        async with UnifiedClient(tonnel_auth="user=...") as client:
            all_listings = await client.fetch_listings(gift_name="Plush Pepe")
            tonnel_only = await client.fetch_listings(venues=["tonnel"])
    """

    def __init__(
        self,
        *,
        tonnel_auth: str = "",
        portals_auth: str = "",
        fragment_auth: str = "",
        timeout: float = 30.0,
    ) -> None:
        self.tonnel = TonnelClient(auth_data=tonnel_auth, timeout=timeout)
        self.portals = PortalsClient(auth_data=portals_auth, timeout=timeout)
        self.fragment = FragmentClient(auth_data=fragment_auth, timeout=timeout)

    async def __aenter__(self) -> UnifiedClient:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        for c in (self.tonnel, self.portals, self.fragment):
            try:
                await c.aclose()
            except Exception:
                pass

    async def fetch_listings(
        self,
        *,
        venues: list[Marketplace] | None = None,
        raise_on_unimplemented: bool = False,
        **kwargs: Any,
    ) -> list[Listing]:
        targets = venues or ["tonnel", "portals", "fragment"]
        results: list[Listing] = []
        for venue in targets:
            client = self._get_client(venue)
            try:
                listings = await client.fetch_listings(**kwargs)
                results.extend(listings)
            except NotImplementedYetError:
                if raise_on_unimplemented:
                    raise
        return results

    async def fetch_floor_stats(
        self,
        *,
        venues: list[Marketplace] | None = None,
        raise_on_unimplemented: bool = False,
    ) -> list[FloorStats]:
        targets = venues or ["tonnel", "portals", "fragment"]
        results: list[FloorStats] = []
        for venue in targets:
            client = self._get_client(venue)
            try:
                stats = await client.fetch_floor_stats()
                results.extend(stats)
            except NotImplementedYetError:
                if raise_on_unimplemented:
                    raise
        return results

    def _get_client(self, venue: Marketplace) -> TonnelClient | PortalsClient | FragmentClient:
        if venue == "tonnel":
            return self.tonnel
        if venue == "portals":
            return self.portals
        if venue == "fragment":
            return self.fragment
        raise ValueError(f"unknown marketplace: {venue!r}")
