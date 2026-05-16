"""Minimal example: fetch floor stats for all Tonnel collections, print top 10 by floor.

Usage:
    export TONNEL_AUTH_DATA="user=...&hash=..."
    python examples/basic_floor_scan.py
"""
from __future__ import annotations

import asyncio
import os

from tg_gifts_sdk import TonnelClient


async def main() -> None:
    auth = os.environ.get("TONNEL_AUTH_DATA", "").strip()
    if not auth:
        raise SystemExit("Set TONNEL_AUTH_DATA env var first.")

    async with TonnelClient(auth_data=auth) as client:
        stats = await client.fetch_floor_stats()

    print(f"Fetched {len(stats)} collections. Top 10 by floor:")
    for s in sorted(stats, key=lambda x: -x.floor)[:10]:
        print(f"  {s.collection:<30} floor={s.floor:>8.2f} TON  "
              f"models={len(s.models)}  backdrops={len(s.backdrops)}  "
              f"symbols={len(s.symbols)}")


if __name__ == "__main__":
    asyncio.run(main())
