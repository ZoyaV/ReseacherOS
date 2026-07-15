"""Parse Hub project URLs and build share links."""

from __future__ import annotations

from typing import Optional
from urllib.parse import parse_qs, urlparse

from hub.app.config import HubConfig
from hub.app.store import HubProject


def parse_hub_project_url(raw: str) -> tuple[str, Optional[str]]:
    """Return (slug, token) from a Hub project URL or path."""
    text = (raw or "").strip()
    if not text:
        raise ValueError("Empty URL")

    if "://" not in text:
        text = "https://placeholder.local" + (text if text.startswith("/") else "/" + text)

    parsed = urlparse(text)
    parts = [p for p in parsed.path.split("/") if p]
    slug: Optional[str] = None
    if "p" in parts:
        idx = parts.index("p")
        if idx + 1 < len(parts):
            slug = parts[idx + 1]
    if not slug:
        raise ValueError("Could not find /p/{slug} in the link")

    token = parse_qs(parsed.query).get("token", [None])[0]
    return slug, token


def project_share_url(config: HubConfig, project: HubProject) -> str:
    base = f"{config.public_url.rstrip('/')}/p/{project.slug}"
    if project.visibility == "unlisted" and project.secret_token:
        return f"{base}?token={project.secret_token}"
    return base


def project_view_href(project: HubProject, token: Optional[str] = None) -> str:
    href = f"/p/{project.slug}"
    if project.visibility == "unlisted":
        tok = token or project.secret_token
        if tok:
            return f"{href}?token={tok}"
    return href
