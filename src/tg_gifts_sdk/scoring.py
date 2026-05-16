"""Trait-aware fair-value scoring.

Many sellers list gifts at the COLLECTION floor, ignoring premium traits
(rare models / backdrops / symbols). This module identifies listings
priced below their trait-aware fair value — a public differentiator vs
naive floor-only bots.

Method (conservative, designed to minimise false positives):
  - Start with collection floor (cheapest combo)
  - Add MAX(model_premium, backdrop_premium, symbol_premium) — assume the
    listing's rarity stacks at most as much as its rarest single trait
  - Discount % = (fair_value - listing.price) / fair_value

Why MAX and not SUM: without joint-distribution data on trait co-occurrence,
summing premiums systematically over-prices listings and creates phantom
deals. MAX is conservative and historically calibrates well in paper testing.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable

    from tg_gifts_sdk.models import FloorStats, Listing


@dataclass(frozen=True)
class FairValueQuote:
    """Estimated fair value for one listing's trait combo, with breakdown."""

    listing: Listing
    fair_value_ton: float
    discount_pct: float
    components: dict[str, float]


def _coerce_stats_index(
    floor_stats: dict[str, FloorStats] | Iterable[FloorStats],
) -> dict[str, FloorStats]:
    """Accept either `dict[collection_name, FloorStats]` or `Iterable[FloorStats]`."""
    if isinstance(floor_stats, dict):
        return floor_stats
    return {s.collection: s for s in floor_stats}


def score_listing(
    listing: Listing,
    floor_stats: dict[str, FloorStats] | Iterable[FloorStats],
) -> FairValueQuote | None:
    """Compute fair value for a listing. Returns None if collection or floor is unknown."""
    stats_index = _coerce_stats_index(floor_stats)
    coll = stats_index.get(listing.gift_name)
    if coll is None:
        return None

    floor = float(coll.floor)
    if floor <= 0:
        return None

    model_floor = float(coll.models.get(listing.model or "", 0))
    backdrop_floor = float(coll.backdrops.get(listing.backdrop or "", 0))
    symbol_floor = float(coll.symbols.get(listing.symbol or "", 0))

    model_prem = max(0.0, model_floor - floor) if model_floor else 0.0
    backdrop_prem = max(0.0, backdrop_floor - floor) if backdrop_floor else 0.0
    symbol_prem = max(0.0, symbol_floor - floor) if symbol_floor else 0.0

    fair_value = floor + max(model_prem, backdrop_prem, symbol_prem)
    if fair_value <= 0:
        return None

    discount = (fair_value - listing.price) / fair_value

    return FairValueQuote(
        listing=listing,
        fair_value_ton=fair_value,
        discount_pct=discount,
        components={
            "floor": floor,
            "model_premium": model_prem,
            "backdrop_premium": backdrop_prem,
            "symbol_premium": symbol_prem,
        },
    )


def find_deals(
    listings: list[Listing],
    floor_stats: dict[str, FloorStats] | Iterable[FloorStats],
    *,
    min_discount: float = 0.10,
) -> list[FairValueQuote]:
    """Return quotes with discount >= min_discount, sorted by discount descending."""
    stats_index = _coerce_stats_index(floor_stats)
    deals: list[FairValueQuote] = []
    for listing in listings:
        quote = score_listing(listing, stats_index)
        if quote is not None and quote.discount_pct >= min_discount:
            deals.append(quote)
    deals.sort(key=lambda q: -q.discount_pct)
    return deals


__all__ = ["FairValueQuote", "score_listing", "find_deals"]
