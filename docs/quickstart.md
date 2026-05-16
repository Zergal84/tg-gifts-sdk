# Quickstart

## 1. Install

```bash
pip install tg-gifts-sdk
```

Requires Python 3.11+.

## 2. Capture `auth_data` (Tonnel)

Tonnel authenticates calls with the URL-encoded Telegram WebApp `initData` string.

1. Open <https://marketplace.tonnel.network> in your browser (log in via Telegram).
2. Open DevTools → Console.
3. Run:

    ```javascript
    localStorage.getItem("web-initData")
    ```

4. Copy the returned string. It looks like `user=%7B%22id%22%3A...&hash=...`.

The string expires every 24–72 hours. Re-capture when API calls start returning 401/403.

## 3. Make your first call

```python
import asyncio
from tg_gifts_sdk import TonnelClient

async def main():
    auth = "user=...&hash=..."
    async with TonnelClient(auth_data=auth) as client:
        balance = await client.fetch_balance()
        print(f"Balance: {balance.balance_ton} TON")
        print(f"Deposit memo: {balance.memo}")

asyncio.run(main())
```

## 4. Browse listings

```python
async with TonnelClient(auth_data=auth) as client:
    listings = await client.fetch_listings(
        gift_name="Plush Pepe",
        sort="price_asc",
        limit=30,
    )
    for item in listings:
        print(f"#{item.gift_num}: {item.price} {item.asset}  model={item.model}  backdrop={item.backdrop}")
```

## 5. Find trait-aware deals

```python
from tg_gifts_sdk import find_deals

async with TonnelClient(auth_data=auth) as client:
    listings = await client.fetch_listings(limit=200)
    stats = await client.fetch_floor_stats()

deals = find_deals(listings, stats, min_discount=0.15)
for d in deals[:5]:
    print(f"{d.listing.gift_name} #{d.listing.gift_num}: "
          f"{d.listing.price} TON  fair~{d.fair_value_ton:.1f}  "
          f"discount {d.discount_pct*100:.1f}%")
```

## Next

- [Floor monitoring tutorial](tutorials/floor-monitoring.md)
- [Arbitrage detection tutorial](tutorials/arbitrage-detection.md)
- [Trait-aware scoring tutorial](tutorials/trait-aware-scoring.md)
