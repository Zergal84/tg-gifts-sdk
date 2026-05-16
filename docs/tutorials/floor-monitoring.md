# Tutorial: Floor monitoring

Track per-collection floor prices over time and alert when one drops below a threshold.

## Setup

```python
import asyncio
import json
from datetime import datetime
from pathlib import Path

from tg_gifts_sdk import TonnelClient

AUTH = "user=...&hash=..."
HISTORY = Path("floor_history.jsonl")

async def snapshot():
    async with TonnelClient(auth_data=AUTH) as client:
        stats = await client.fetch_floor_stats()
    row = {
        "ts": datetime.utcnow().isoformat(),
        "floors": {s.collection: s.floor for s in stats},
    }
    with HISTORY.open("a") as f:
        f.write(json.dumps(row) + "\n")
    return row

asyncio.run(snapshot())
```

Run this every 5 minutes via cron, systemd timer, or a simple `while True: await asyncio.sleep(300)` loop.

## Alert on drops

```python
async def check_for_drops(threshold_pct: float = 0.10):
    rows = [json.loads(line) for line in HISTORY.read_text().splitlines()]
    if len(rows) < 2:
        return

    latest = rows[-1]["floors"]
    prior = rows[-2]["floors"]
    for coll, new_floor in latest.items():
        old_floor = prior.get(coll)
        if old_floor is None or old_floor == 0:
            continue
        drop = (old_floor - new_floor) / old_floor
        if drop >= threshold_pct:
            print(f"FLOOR DROP: {coll} from {old_floor} to {new_floor} ({drop*100:.1f}%)")
```

Pipe `check_for_drops()` output to your favourite alerter (Telegram bot, Slack webhook, Pushover) and you have a basic floor monitor.
