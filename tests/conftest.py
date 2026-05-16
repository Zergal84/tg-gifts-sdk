"""Shared pytest fixtures."""
from __future__ import annotations

import os

import pytest


@pytest.fixture
def tonnel_auth_data_or_skip() -> str:
    """Return TONNEL_AUTH_DATA env or skip the test if it is not set."""
    value = os.getenv("TONNEL_AUTH_DATA", "").strip()
    if not value:
        pytest.skip("TONNEL_AUTH_DATA not set — skipping live integration test")
    return value
