# Tutorial: Trait-aware scoring

Many sellers list gifts at the **collection floor** price, ignoring the premium that rare models, backdrops, or symbols command. A naive bot that compares only against collection floor will miss these. `tg-gifts-sdk` ships a trait-aware scorer that catches them.

## How it works

For each listing:

1. Look up the collection floor from `FloorStats`.
2. Look up the per-trait floors for the listing's specific model / backdrop / symbol.
3. Compute the premium each trait adds (`trait_floor - collection_floor`, clamped at 0).
4. **Fair value = collection_floor + max(model_premium, backdrop_premium, symbol_premium).**
5. **Discount % = (fair_value - listing.price) / fair_value.**

The MAX-of-premiums approach is conservative: without joint-distribution data on which traits co-occur, summing all premiums systematically over-prices listings and creates phantom deals. MAX undercounts in some cases but rarely false-positives.

## Example

```python
import asyncio
from tg_gifts_sdk import TonnelClient, find_deals

AUTH = "user=...&hash=..."

async def main():
    async with TonnelClient(auth_data=AUTH) as client:
        listings = await client.fetch_listings(gift_name="Plush Pepe", limit=100)
        stats = await client.fetch_floor_stats()

    deals = find_deals(listings, stats, min_discount=0.15)

    for d in deals:
        item = d.listing
        c = d.components
        print(f"#{item.gift_num}: {item.price} TON  fair~{d.fair_value_ton:.1f}  "
              f"({d.discount_pct*100:.1f}% discount)")
        print(f"  Components: floor={c['floor']} "
              f"model_prem={c['model_premium']} "
              f"backdrop_prem={c['backdrop_premium']} "
              f"symbol_prem={c['symbol_premium']}")

asyncio.run(main())
```

## Tuning

The `min_discount` threshold controls false-positive rate:
- `0.10` (10%) — looser, more deals, more noise
- `0.15` (15%) — moderate, good starting point for paper testing
- `0.25` (25%) — tight, only obvious mispricings, fewer alerts

In production, calibrate by running paper-mode for a week and measuring: how many alerts converted to profitable buys vs noise.

## When SUM beats MAX

If you've gathered joint-distribution data and confirmed premium traits do stack additively in your collections of interest, you can write a custom scorer:

```python
from tg_gifts_sdk import FloorStats, Listing
from tg_gifts_sdk.scoring import FairValueQuote

def sum_score_listing(listing: Listing, stats: dict[str, FloorStats]) -> FairValueQuote | None:
    coll = stats.get(listing.gift_name)
    if coll is None or coll.floor <= 0:
        return None
    floor = coll.floor
    premiums = {
        "model": max(0, coll.models.get(listing.model or "", 0) - floor),
        "backdrop": max(0, coll.backdrops.get(listing.backdrop or "", 0) - floor),
        "symbol": max(0, coll.symbols.get(listing.symbol or "", 0) - floor),
    }
    fair = floor + sum(premiums.values())
    return FairValueQuote(
        listing=listing,
        fair_value_ton=fair,
        discount_pct=(fair - listing.price) / fair,
        components={"floor": floor, **{f"{k}_premium": v for k, v in premiums.items()}},
    )
```

Drop-in replacement, same return shape.
