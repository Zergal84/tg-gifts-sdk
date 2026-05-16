# Contributing to tg-gifts-sdk

## Welcome contributions

The fastest path to v1.0 is filling in the Portals and Fragment adapters. They currently raise `NotImplementedYetError` — the goal is to bring them up to parity with TonnelClient.

## What we need

### Portals
1. Working `fetch_listings(...)` against `https://portals-market.com/api` (or whatever the live base URL is).
2. Working `fetch_floor_stats()` if Portals exposes equivalent endpoints.
3. Tests using `respx` or monkeypatched `_http.post_json`, no live network in CI.

### Fragment
1. Working GraphQL client against `https://fragment.com/api` for gift listings.
2. Handling of Fragment's CSRF token rotation.
3. Tests as above.

### To prepare an API capture

1. Open the marketplace in your browser, log in.
2. Open DevTools → Network tab.
3. Trigger the action you want to capture (browse listings, search, view stats).
4. Right-click the matching request → Copy → Copy as cURL.
5. Paste in a GitHub issue, redact any session-specific tokens or addresses.

## Dev setup

```bash
git clone https://github.com/Zergal84/tg-gifts-sdk
cd tg-gifts-sdk
python -m venv .venv
source .venv/bin/activate    # or .venv\Scripts\activate on Windows
pip install -e ".[dev]"
pre-commit install
```

## Code style

- `ruff check src tests` — must pass
- `mypy` — must pass (strict mode)
- `pytest -v` — must pass; new functionality requires new tests
- Test files use `pytest.mark.asyncio` for async tests; integration tests marked with `pytest.mark.integration` (skipped unless explicit env var set)

## Commits

We follow Conventional Commits:
- `feat:` new functionality
- `fix:` bug fix
- `docs:` documentation only
- `test:` test changes only
- `chore:` build/CI/tooling
- `refactor:` code change that doesn't add or fix functionality
