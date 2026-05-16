"""SDK-specific exceptions."""
from __future__ import annotations


class TgGiftsSdkError(Exception):
    """Base class for all SDK errors."""


class MarketplaceUnavailableError(TgGiftsSdkError):
    """The marketplace returned an error response (4xx/5xx, CloudFlare block, etc.)."""

    def __init__(self, marketplace: str, status_code: int | None, body: str = "") -> None:
        self.marketplace = marketplace
        self.status_code = status_code
        self.body = body[:500]
        super().__init__(
            f"{marketplace} returned {status_code}: {self.body!r}"
        )


class AuthDataMissingError(TgGiftsSdkError):
    """A client method requiring authentication was called without auth_data."""


class NotImplementedYetError(TgGiftsSdkError, NotImplementedError):
    """Stub marker: the requested capability is scaffolded but not implemented yet."""

    def __init__(self, marketplace: str, operation: str, hint: str = "") -> None:
        self.marketplace = marketplace
        self.operation = operation
        self.hint = hint
        msg = f"{marketplace}.{operation} is not implemented yet"
        if hint:
            msg += f" — {hint}"
        super().__init__(msg)
