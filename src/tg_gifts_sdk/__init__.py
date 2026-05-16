"""tg-gifts-sdk — unified async Python SDK for Telegram Gifts marketplaces."""
from __future__ import annotations

from tg_gifts_sdk.exceptions import (
    AuthDataMissingError,
    MarketplaceUnavailableError,
    NotImplementedYetError,
    TgGiftsSdkError,
)
from tg_gifts_sdk.fragment import FragmentClient
from tg_gifts_sdk.models import FloorStats, Gift, Listing, Marketplace, Trait
from tg_gifts_sdk.portals import PortalsClient
from tg_gifts_sdk.tonnel import BalanceInfo, TonnelClient
from tg_gifts_sdk.unified import UnifiedClient

__version__ = "0.1.0"

__all__ = [
    "FloorStats", "Gift", "Listing", "Marketplace", "Trait",
    "TonnelClient", "PortalsClient", "FragmentClient", "UnifiedClient",
    "BalanceInfo",
    "TgGiftsSdkError", "MarketplaceUnavailableError",
    "AuthDataMissingError", "NotImplementedYetError",
    "__version__",
]
