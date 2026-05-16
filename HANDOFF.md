# tg-gifts-sdk handoff

**Status:** local build complete, ready for first GH push + PyPI publish.

## What's in here

- Single-package Python SDK targeting bounty #1229.
- Tonnel client fully working (read-only): listings, floor stats, balance.
- Portals + Fragment stubs raising `NotImplementedYetError`.
- UnifiedClient aggregator that gracefully skips unimplemented venues.
- Trait-aware scoring module (your public differentiator).
- Pydantic v2 typed models.
- 37 unit tests passing + 3 live smoke tests (skip unless TONNEL_AUTH_DATA set).
- mypy strict + ruff clean.
- GitHub Actions CI matrix on Python 3.11/3.12/3.13.
- mkdocs-material site with quickstart + 3 tutorials.
- Apache 2.0.

## Pre-push checklist

1. **Delete this file before push:** `rm HANDOFF.md`. It exposes nothing sensitive but it's operator-only context.

2. **Create empty GH repo `Zergal84/tg-gifts-sdk`** via web UI:
    - Public.
    - Don't initialise with README/LICENSE/gitignore (we have them locally).
    - Set description: "Unified async Python SDK for Telegram Gifts marketplaces (Tonnel, Portals, Fragment)"
    - Add topics: `telegram`, `gifts`, `ton`, `tonnel`, `marketplace`, `async`, `python`, `sdk`

3. **Add remote and push:**

    ```bash
    cd "C:/Users/User/Claude Code/tg-gifts-sdk"
    git remote add origin git@github.com:Zergal84/tg-gifts-sdk.git
    git push -u origin main
    ```

4. **Enable GitHub Pages for docs (optional, can defer):**
    - Settings → Pages → Source: GitHub Actions
    - Will need an additional workflow to deploy mkdocs build; not blocking for bounty submission.

5. **Publish to PyPI:**

    ```bash
    cd "C:/Users/User/Claude Code/tg-gifts-sdk"
    .venv/Scripts/python.exe -m build
    .venv/Scripts/twine.exe upload dist/*
    ```

    Requires PyPI account + API token. Token goes in `~/.pypirc` or via prompts.

6. **Post submission comment on TON Society issue #1229** (English, factual, mirrors prior takedown tone):

    ```markdown
    Submitting `tg-gifts-sdk` for bounty #1229.

    Repository: https://github.com/Zergal84/tg-gifts-sdk
    PyPI: https://pypi.org/project/tg-gifts-sdk/0.1.0/

    Scope of v0.1.0:
    - `TonnelClient`: working async client with listings, floor stats, balance — uses curl_cffi Firefox 133 impersonation against the live `gifts2.tonnel.network` API
    - `PortalsClient`, `FragmentClient`: interface stubs raising `NotImplementedYetError` with documented hints for contributors
    - `UnifiedClient`: aggregator across venues, configurable behaviour for unimplemented venues
    - `tg_gifts_sdk.scoring`: trait-aware fair-value scorer with MAX-premium method (calibrated against weeks of paper trading)
    - Pydantic v2 typed models: `Listing`, `Gift`, `FloorStats`, `Trait`, `BalanceInfo`
    - 37 unit tests + 3 live integration smoke tests
    - mypy strict + ruff clean
    - GitHub Actions CI on Python 3.11, 3.12, 3.13
    - mkdocs-material documentation site with quickstart + 3 tutorials
    - Apache 2.0 license

    Notes:
    - Write operations (`buyGift`, `listGift`) are deliberately out of scope to keep the public SDK conservative.
    - Portals and Fragment are scaffolded with `NotImplementedYetError`; bringing them up to parity is contribution-tier work and tracked in CONTRIBUTING.md. I'd rather ship honest stubs than fake implementations.

    Prior art (referenced in the proposal): https://github.com/Zergal84/tonnel-scanner-demo published 2026-05-14 before this issue was filed.

    Ready for review.
    ```

7. **Update Lane B proposal-A draft (in polymarket repo):**

    The `hustle/lane_b/proposal_drafts/proposal-A-tg-gifts-sdk-v3.md` should reflect that this is no longer a "Lane A → exploration → eventual SDK" pitch but "delivered v0.1.0, contribution-ready for Portals + Fragment".

## What's intentionally missing

- Auth refresh helpers (no Pyrogram dependency to stay light).
- Rate limiting (Tonnel doesn't enforce hard limits at v0.1.0 cadence).
- WebSocket subscriptions (Tonnel doesn't expose any).
- Write operations.
- Portals + Fragment implementations (stubs only).
- Type-stub package for static analysis without runtime install (PEP 561 marker present in source).
