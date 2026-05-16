"""Trait-aware deal detector against Tonnel listings.

Usage:
    export TONNEL_AUTH_DATA="user=...&hash=..."
    python examples/deal_detector.py "Plush Pepe" "Crystal Ball"
"""
from __future__ import annotations

import asyncio
import os
import sys

from tg_gifts_sdk import TonnelClient, find_deals


MIN_DISCOUNT = 0.15


async def main(collections: list[str]) -> None:
    auth = os.environ.get("TONNEL_AUTH_DATA", "").strip()
    if not auth:
        raise SystemExit("Set TONNEL_AUTH_DATA env var first.")

    async with TonnelClient(auth_data=auth) as client:
        stats = await client.fetch_floor_stats()
        all_listings = []
        for coll in collections:
            listings = await client.fetch_listings(gift_name=coll, limit=50)
            all_listings.extend(listings)

    deals = find_deals(all_listings, stats, min_discount=MIN_DISCOUNT)
    print(f"Found {len(deals)} deals at >= {MIN_DISCOUNT*100:.0f}% discount:")
    for d in deals:
        item = d.listing
        print(f"  {item.gift_name} #{item.gift_num:>5}: {item.price:>8.2f} TON  "
              f"fair~{d.fair_value_ton:>8.2f}  ({d.discount_pct*100:>5.1f}% off)")
        print(f"    model={item.model!r:<25} backdrop={item.backdrop!r:<25} symbol={item.symbol!r}")


if __name__ == "__main__":
    args = sys.argv[1:] or ["Plush Pepe", "Crystal Ball"]
    asyncio.run(main(args))
