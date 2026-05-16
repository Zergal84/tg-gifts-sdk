# Tutorial: Arbitrage detection (cross-venue)

When Portals and Fragment adapters land, the same listing can show up at different prices across venues. This tutorial sketches the pattern; today only Tonnel is wired up, so it runs read-only on Tonnel and flags listings priced below their trait-aware fair value.

## Implementation (Tonnel today, multi-venue later)

```python
import asyncio

from tg_gifts_sdk import TonnelClient, find_deals

AUTH = "user=...&hash=..."
MONITORED = ["Plush Pepe", "Durov's Cap", "Statue of Liberty", "Crystal Ball"]

async def scan_once():
    async with TonnelClient(auth_data=AUTH) as client:
        stats = await client.fetch_floor_stats()
        all_listings = []
        for collection in MONITORED:
            listings = await client.fetch_listings(gift_name=collection, limit=50)
            all_listings.extend(listings)

    deals = find_deals(all_listings, stats, min_discount=0.15)
    return deals

deals = asyncio.run(scan_once())
for d in deals:
    print(f"{d.listing.gift_name} #{d.listing.gift_num}: "
          f"{d.listing.price} TON  fair~{d.fair_value_ton:.1f}  "
          f"({d.discount_pct*100:.1f}% discount)")
```

## When Portals and Fragment land

```python
from collections import defaultdict
from tg_gifts_sdk import UnifiedClient

async def scan_all_venues():
    async with UnifiedClient(
        tonnel_auth="...",
        portals_auth="...",
        fragment_auth="...",
    ) as client:
        listings = await client.fetch_listings(gift_name="Plush Pepe", limit=200)

    by_gift = defaultdict(list)
    for item in listings:
        by_gift[(item.gift_name, item.gift_num)].append(item)

    for key, group in by_gift.items():
        if len(group) > 1:
            prices = sorted([(item.price, item.marketplace) for item in group])
            cheapest = prices[0]
            most_expensive = prices[-1]
            spread = most_expensive[0] - cheapest[0]
            if spread > 0:
                print(f"{key}: buy at {cheapest[1]} for {cheapest[0]} TON, "
                      f"sell at {most_expensive[1]} for {most_expensive[0]} TON "
                      f"(spread {spread} TON)")
```

This will start working unmodified the moment Portals/Fragment adapters land. Track [GitHub issues](https://github.com/Zergal84/tg-gifts-sdk/issues) for adapter progress.
