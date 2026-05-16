"""Trait-aware scoring tests — pure functions."""
from __future__ import annotations

import pytest

from tg_gifts_sdk import FloorStats, Listing
from tg_gifts_sdk.scoring import FairValueQuote, find_deals, score_listing


def _listing(*, price: float, model: str | None = None, backdrop: str | None = None,
             symbol: str | None = None, name: str = "Plush Pepe") -> Listing:
    return Listing(
        marketplace="tonnel",
        gift_id=1, gift_name=name, gift_num=1,
        price=price, asset="TON",
        model=model, backdrop=backdrop, symbol=symbol,
        raw={},
    )


def _stats(*, floor: float, models: dict[str, float] | None = None,
           backdrops: dict[str, float] | None = None,
           symbols: dict[str, float] | None = None,
           name: str = "Plush Pepe") -> FloorStats:
    return FloorStats(
        marketplace="tonnel", collection=name, floor=floor,
        models=models or {}, backdrops=backdrops or {}, symbols=symbols or {},
    )


def test_score_unknown_collection_returns_none() -> None:
    listing = _listing(price=10.0)
    stats_index = {"Other Collection": _stats(floor=100)}
    assert score_listing(listing, stats_index) is None


def test_score_zero_floor_returns_none() -> None:
    listing = _listing(price=10.0)
    stats_index = {"Plush Pepe": _stats(floor=0)}
    assert score_listing(listing, stats_index) is None


def test_score_with_only_floor_no_premium() -> None:
    listing = _listing(price=80.0)
    stats_index = {"Plush Pepe": _stats(floor=100)}
    quote = score_listing(listing, stats_index)
    assert quote is not None
    assert quote.fair_value_ton == 100.0
    assert abs(quote.discount_pct - 0.20) < 1e-9
    assert quote.components["floor"] == 100.0
    assert quote.components["model_premium"] == 0.0


def test_score_with_rare_model_adds_premium() -> None:
    listing = _listing(price=400.0, model="Diamond")
    stats_index = {"Plush Pepe": _stats(
        floor=100, models={"Diamond": 1000, "Gold": 500, "Common": 100}
    )}
    quote = score_listing(listing, stats_index)
    assert quote is not None
    assert quote.fair_value_ton == 1000.0
    assert quote.components["model_premium"] == 900.0


def test_score_takes_max_of_premiums_conservative() -> None:
    listing = _listing(
        price=500.0, model="Diamond", backdrop="Pink", symbol="Crown",
    )
    stats_index = {"Plush Pepe": _stats(
        floor=100,
        models={"Diamond": 600},
        backdrops={"Pink": 800},
        symbols={"Crown": 500},
    )}
    quote = score_listing(listing, stats_index)
    assert quote is not None
    assert quote.fair_value_ton == 800.0
    assert quote.components["backdrop_premium"] == 700.0


def test_find_deals_filters_by_min_discount() -> None:
    listings = [
        _listing(price=80.0),
        _listing(price=95.0),
        _listing(price=70.0),
    ]
    stats_index = {"Plush Pepe": _stats(floor=100)}
    deals = find_deals(listings, stats_index, min_discount=0.10)
    assert len(deals) == 2
    assert deals[0].discount_pct > deals[1].discount_pct
    assert abs(deals[0].discount_pct - 0.30) < 1e-9


def test_find_deals_skips_listings_for_unknown_collections() -> None:
    listings = [_listing(price=80.0, name="UnknownCollection")]
    stats_index = {"Plush Pepe": _stats(floor=100)}
    deals = find_deals(listings, stats_index, min_discount=0.10)
    assert deals == []


def test_find_deals_accepts_stats_as_list_or_dict() -> None:
    listings = [_listing(price=70.0)]
    as_list = [_stats(floor=100)]
    as_dict = {"Plush Pepe": _stats(floor=100)}

    deals_list = find_deals(listings, as_list, min_discount=0.10)
    deals_dict = find_deals(listings, as_dict, min_discount=0.10)

    assert len(deals_list) == 1
    assert len(deals_dict) == 1
    assert deals_list[0].fair_value_ton == deals_dict[0].fair_value_ton


def test_fair_value_quote_components_keys() -> None:
    listing = _listing(price=80.0, model="Diamond")
    stats_index = {"Plush Pepe": _stats(floor=100, models={"Diamond": 200})}
    quote = score_listing(listing, stats_index)
    assert quote is not None
    assert set(quote.components.keys()) == {
        "floor", "model_premium", "backdrop_premium", "symbol_premium"
    }
