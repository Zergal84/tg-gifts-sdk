"""Unified Pydantic v2 models for Telegram Gifts marketplaces.

Each marketplace adapter parses raw responses into these typed shapes,
so callers see a consistent surface regardless of venue.
"""
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

Marketplace = Literal["tonnel", "portals", "fragment"]


class Trait(BaseModel):
    """A single trait variant (model / backdrop / symbol) with rarity + floor."""

    model_config = ConfigDict(frozen=True)

    category: Literal["model", "backdrop", "symbol"]
    name: str
    rarity_pct: float | None = None
    floor: float | None = None


class Gift(BaseModel):
    """A Telegram gift identifier — owned, held, or listed.

    Use `Listing` for sale-side data (price, seller, asset).
    """

    model_config = ConfigDict(frozen=False)

    marketplace: Marketplace
    gift_id: int
    gift_name: str
    gift_num: int

    model: str | None = None
    backdrop: str | None = None
    symbol: str | None = None

    owner: str | None = None


class Listing(BaseModel):
    """A gift currently for sale on a marketplace."""

    model_config = ConfigDict(frozen=False)

    marketplace: Marketplace
    gift_id: int
    gift_name: str
    gift_num: int

    price: float
    asset: Literal["TON", "USDT", "TONNEL"] = "TON"

    model: str | None = None
    backdrop: str | None = None
    symbol: str | None = None
    seller: str | None = None

    raw: dict[str, Any] = Field(default_factory=dict)

    @field_validator("price")
    @classmethod
    def _price_non_negative(cls, v: float) -> float:
        if v < 0:
            raise ValueError("price must be >= 0")
        return v

    @property
    def trait_signature(self) -> tuple[str, str | None, str | None, str | None]:
        """Composite key used by trait-aware scoring (`scoring` module)."""
        return (self.gift_name, self.model, self.backdrop, self.symbol)


class FloorStats(BaseModel):
    """Per-collection floor + per-trait floors snapshot."""

    model_config = ConfigDict(frozen=False)

    marketplace: Marketplace
    collection: str
    floor: float
    models: dict[str, float] = Field(default_factory=dict)
    backdrops: dict[str, float] = Field(default_factory=dict)
    symbols: dict[str, float] = Field(default_factory=dict)


__all__ = ["Trait", "Gift", "Listing", "FloorStats", "Marketplace"]
