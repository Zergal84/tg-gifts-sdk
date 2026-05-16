"""Internal HTTP helpers. Not part of public API.

Tonnel requires curl_cffi TLS impersonation (Firefox 133) to bypass
CloudFlare. We wrap the sync curl_cffi call in `asyncio.to_thread` to
expose an async surface from the otherwise-sync library.
"""
from __future__ import annotations

import asyncio
from typing import Any

from tenacity import retry as _tenacity_retry
from tenacity import (
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

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


class _TransientServerError(Exception):
    """Raised internally to drive tenacity retry on 5xx responses."""

    def __init__(self, status_code: int) -> None:
        self.status_code = status_code
        super().__init__(f"transient server error {status_code}")


def build_firefox_headers(*, origin: str, host: str | None = None) -> dict[str, str]:
    """Headers replicating a real Firefox 133 cross-site fetch.

    Required to satisfy Tonnel's CloudFlare rules (chrome120 and Firefox <100
    impersonations get 403).
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
    proxy: str | None = None,
    max_retries: int = 2,
) -> tuple[int, dict[str, Any] | list[Any] | str]:
    """Async wrapper around curl_cffi.requests.post.

    Retries on 5xx with tenacity exponential backoff when ``max_retries > 0``.
    Routes through `proxy` (single URL applied to both http and https) when set.
    """
    proxies = {"http": proxy, "https": proxy} if proxy else None

    def _do_raw() -> tuple[int, Any]:
        resp = curl_requests.post(
            url, json=json_body, headers=headers,
            impersonate=impersonate, timeout=timeout,  # type: ignore[arg-type]
            proxies=proxies,  # type: ignore[arg-type]
        )
        try:
            return resp.status_code, resp.json()  # type: ignore[no-untyped-call]
        except Exception:
            return resp.status_code, resp.text[:500]

    if max_retries <= 0:
        return await asyncio.to_thread(_do_raw)

    @_tenacity_retry(
        stop=stop_after_attempt(max_retries + 1),
        wait=wait_exponential(multiplier=0.5, min=0.5, max=8),
        retry=retry_if_exception_type(_TransientServerError),
        reraise=True,
    )
    def _do_with_retry() -> tuple[int, Any]:
        status, body = _do_raw()
        if 500 <= status < 600:
            raise _TransientServerError(status)
        return status, body

    try:
        return await asyncio.to_thread(_do_with_retry)
    except _TransientServerError as e:
        return e.status_code, ""
