"""Shared httpx client settings for GitHub API calls."""

from __future__ import annotations

import os
from typing import Any

import httpx


def github_http_client(**kwargs: Any) -> httpx.AsyncClient:
    """Build httpx client for GitHub.

    Default: direct connection (ignore system proxy that often returns 403).
    Set HUB_GITHUB_NETWORK=system to use HTTP(S)_PROXY from environment.
    Set HUB_HTTPS_PROXY=http://... to force a specific proxy.
    """
    timeout = kwargs.pop("timeout", 30.0)
    mode = os.environ.get("HUB_GITHUB_NETWORK", "direct").strip().lower()
    explicit_proxy = os.environ.get("HUB_HTTPS_PROXY") or os.environ.get("HUB_HTTP_PROXY")

    if explicit_proxy:
        return httpx.AsyncClient(
            timeout=timeout,
            trust_env=False,
            proxy=explicit_proxy,
            **kwargs,
        )

    if mode == "system":
        return httpx.AsyncClient(timeout=timeout, trust_env=True, **kwargs)

    return httpx.AsyncClient(timeout=timeout, trust_env=False, **kwargs)


async def github_request(method: str, url: str, **kwargs: Any) -> httpx.Response:
    """Try direct GitHub request, then fall back to system proxy if needed."""
    timeout = kwargs.pop("timeout", 60.0)
    errors: list[str] = []
    for trust_env in (False, True):
        label = "system-proxy" if trust_env else "direct"
        try:
            async with httpx.AsyncClient(timeout=timeout, trust_env=trust_env) as client:
                response = await client.request(method, url, **kwargs)
                return response
        except httpx.HTTPError as exc:
            errors.append(f"{label}: {exc}")
    raise httpx.HTTPError("; ".join(errors))
