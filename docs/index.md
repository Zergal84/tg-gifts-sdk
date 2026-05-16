# tg-gifts-sdk

Unified async Python SDK for the Telegram Gifts marketplaces — **Tonnel**, **Portals**, and **Fragment**.

## What it does today

| Capability | Tonnel | Portals | Fragment |
|---|---|---|---|
| Read listings | ✅ | scaffolded | scaffolded |
| Read floor stats | ✅ | scaffolded | scaffolded |
| Read account balance | ✅ | — | — |
| Trait-aware scoring | ✅ (venue-agnostic) | — | — |
| Write (buy/sell) | — (out of scope) | — | — |

**Tonnel works end-to-end.** Portals and Fragment are interface stubs awaiting contributions.

## Install

```bash
pip install tg-gifts-sdk
```

## In 30 seconds

```python
import asyncio
from tg_gifts_sdk import TonnelClient, find_deals

async def main():
    async with TonnelClient(auth_data="user=...&hash=...") as client:
        listings = await client.fetch_listings(gift_name="Plush Pepe", limit=50)
        stats = await client.fetch_floor_stats()

    for d in find_deals(listings, stats, min_discount=0.15):
        print(f"{d.listing.gift_name} #{d.listing.gift_num}: "
              f"{d.listing.price} TON, {d.discount_pct*100:.1f}% below fair")

asyncio.run(main())
```

See [Quickstart](quickstart.md) for installation, auth capture, and the full API surface.
