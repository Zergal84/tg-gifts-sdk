"""tg-gifts-sdk — unified async Python SDK for Telegram Gifts marketplaces."""
from __future__ import annotations

from tg_gifts_sdk.exceptions import (
    AuthDataMissingError,
    MarketplaceUnavailableError,
    NotImplementedYetError,
    TgGiftsSdkError,
)
from tg_gifts_sdk.models import FloorStats, Gift, Listing, Marketplace, Trait

__version__ = "0.1.0"

__all__ = [
    "FloorStats", "Gift", "Listing", "Marketplace", "Trait",
    "TgGiftsSdkError", "MarketplaceUnavailableError",
    "AuthDataMissingError", "NotImplementedYetError",
    "__version__",
]
