# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] — 2026-05-16

### Added
- `TonnelClient` — async read-only client for the Tonnel marketplace:
  - `fetch_listings()` with full filter set (gift_name, model, backdrop, symbol, sort, pagination)
  - `fetch_floor_stats()` returning per-collection + per-trait floor data
  - `fetch_balance()` returning operator balance + deposit memo
- `PortalsClient`, `FragmentClient` — interface stubs raising `NotImplementedYetError` with hints
- `UnifiedClient` — aggregator across all venues, with `raise_on_unimplemented` control
- Pydantic v2 models: `Listing`, `Gift`, `FloorStats`, `Trait`, `BalanceInfo`
- `tg_gifts_sdk.scoring`:
  - `score_listing()` — trait-aware fair-value scorer (conservative MAX-premium method)
  - `find_deals()` — filter listings by min discount, sorted by discount descending
- SDK-specific exceptions: `TgGiftsSdkError`, `MarketplaceUnavailableError`, `AuthDataMissingError`, `NotImplementedYetError`
- GitHub Actions CI (Python 3.11/3.12/3.13, ruff, mypy strict, pytest)
- mkdocs-material documentation site
- Live integration smoke test (skipped by default; runs when `TONNEL_AUTH_DATA` env is set)

### Notes
- Write operations (`buyGift`, `listGift`) deliberately not implemented — out of scope for the public SDK.
- Portals and Fragment adapters require contribution; see CONTRIBUTING.md.
