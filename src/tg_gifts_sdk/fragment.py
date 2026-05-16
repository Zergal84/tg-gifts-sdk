"""Fragment marketplace client — interface stub.

Status: scaffolded; not implemented yet.

Fragment (https://fragment.com) is Telegram's official auction venue for
usernames, numbers, and collectible gifts. Public web pages expose
GraphQL-like queries; an unofficial reverse-engineering effort is needed
to expose a clean SDK surface here.

If you want to contribute a working implementation, see CONTRIBUTING.md.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from tg_gifts_sdk.exceptions import NotImplementedYetError

if TYPE_CHECKING:
    from types import TracebackType

    from tg_gifts_sdk.models import FloorStats, Listing


class FragmentClient:
    """Async client stub for the Fragment marketplace.

    All methods raise `NotImplementedYetError`. Surface mirrors `TonnelClient`
    so `UnifiedClient` can aggregate across venues once filled in.
    """

    def __init__(self, *, auth_data: str = "", timeout: float = 30.0) -> None:
        self.auth_data = auth_data
        self.timeout = timeout

    async def __aenter__(self) -> FragmentClient:
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
            marketplace="fragment",
            operation="fetch_listings",
            hint="Fragment uses a GraphQL endpoint at https://fragment.com/api with "
                 "rotating CSRF tokens. Contributions welcome — see CONTRIBUTING.md.",
        )

    async def fetch_floor_stats(self) -> list[FloorStats]:
        raise NotImplementedYetError(
            marketplace="fragment",
            operation="fetch_floor_stats",
            hint="Fragment GraphQL not yet reverse-engineered.",
        )
