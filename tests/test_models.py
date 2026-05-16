"""Pydantic model tests — round-trip + validation."""
from __future__ import annotations

import pytest

from tg_gifts_sdk.models import FloorStats, Gift, Listing, Trait


def test_listing_minimal_construction() -> None:
    listing = Listing(
        marketplace="tonnel",
        gift_id=12345,
        gift_name="Plush Pepe",
        gift_num=42,
        price=800.0,
        asset="TON",
        raw={},
    )
    assert listing.marketplace == "tonnel"
    assert listing.gift_id == 12345
    assert listing.price == 800.0
    assert listing.model is None


def test_listing_with_traits() -> None:
    listing = Listing(
        marketplace="tonnel",
        gift_id=1, gift_name="Plush Pepe", gift_num=1,
        price=1000.0, asset="TON",
        model="Diamond (5%)", backdrop="Pink (10%)", symbol="Crown (3%)",
        seller="UQABC", raw={},
    )
    assert listing.trait_signature == ("Plush Pepe", "Diamond (5%)", "Pink (10%)", "Crown (3%)")


def test_listing_serialises_to_dict() -> None:
    listing = Listing(
        marketplace="tonnel",
        gift_id=1, gift_name="X", gift_num=1,
        price=10.0, asset="TON", raw={"a": 1},
    )
    d = listing.model_dump()
    assert d["marketplace"] == "tonnel"
    assert d["raw"] == {"a": 1}


def test_floor_stats_construction() -> None:
    stats = FloorStats(
        marketplace="tonnel",
        collection="Plush Pepe",
        floor=800.0,
        models={"Diamond": 5000.0, "Gold": 3000.0},
        backdrops={"Pink": 6000.0},
        symbols={},
    )
    assert stats.floor == 800.0
    assert stats.models["Diamond"] == 5000.0


def test_trait_construction() -> None:
    t = Trait(category="model", name="Diamond", rarity_pct=5.0, floor=5000.0)
    assert t.category == "model"
    assert t.rarity_pct == 5.0


def test_gift_construction() -> None:
    g = Gift(
        marketplace="tonnel",
        gift_id=1, gift_name="Plush Pepe", gift_num=42,
    )
    assert g.gift_id == 1
    assert g.model is None


def test_listing_rejects_negative_price() -> None:
    with pytest.raises(ValueError):
        Listing(
            marketplace="tonnel",
            gift_id=1, gift_name="X", gift_num=1,
            price=-10.0, asset="TON", raw={},
        )


def test_floor_stats_rejects_unknown_marketplace() -> None:
    with pytest.raises(ValueError):
        FloorStats(
            marketplace="unknown_market",
            collection="X", floor=1.0,
            models={}, backdrops={}, symbols={},
        )
