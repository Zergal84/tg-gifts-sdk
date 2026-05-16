"""Internal HTTP helpers. Not part of public API.

Tonnel requires curl_cffi TLS impersonation (Firefox 133) to bypass
CloudFlare. We wrap the sync curl_cffi call in `asyncio.to_thread` to
expose an async surface from the otherwise-sync library.
"""
from __future__ import annotations

import asyncio
from typing import Any

try:
    from curl_cffi import requests as curl_requests
except ImportError as e:
    raise ImportError(
        "curl_cffi is required for Tonnel client. "
        "Install with: pip install 'tg-gifts-sdk[default]' or pip install curl_cffi"
    ) from e


_FIREFOX_133_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) "
    "Gecko/20100101 Firefox/133.0"
)


def build_firefox_headers(*, origin: str, host: str | None = None) -> dict[str, str]:
    """Headers replicating a real Firefox 133 cross-site fetch.

    Required to satisfy Tonnel's CloudFlare rules — chrome120 and Firefox <100
    impersonations get 403.
    """
    headers = {
        "User-Agent": _FIREFOX_133_UA,
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Content-Type": "application/json",
        "Referer": f"{origin}/",
        "Origin": origin,
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
    }
    if host is not None:
        headers["authority"] = host
    return headers


async def post_json(
    url: str,
    *,
    json_body: dict[str, Any],
    headers: dict[str, str],
    impersonate: str = "firefox133",
    timeout: float = 30.0,  # noqa: ASYNC109 — sync timeout forwarded to curl_cffi, not asyncio
) -> tuple[int, dict[str, Any] | list[Any] | str]:
    """Async wrapper around curl_cffi.requests.post — returns (status, json-or-text)."""

    def _do() -> tuple[int, Any]:
        resp = curl_requests.post(
            url, json=json_body, headers=headers,
            impersonate=impersonate,  # type: ignore[arg-type]
            timeout=timeout,
        )
        try:
            return resp.status_code, resp.json()  # type: ignore[no-untyped-call]
        except Exception:
            return resp.status_code, resp.text[:500]

    return await asyncio.to_thread(_do)
