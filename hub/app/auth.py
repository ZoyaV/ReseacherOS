"""GitHub OAuth and signed session cookies."""

from __future__ import annotations

import secrets
from typing import Optional
from urllib.parse import urlencode

import httpx
from fastapi import HTTPException, Request, Response
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from hub.app.config import HubConfig
from hub.app.github_http import github_http_client, github_request
from hub.app.github_client import GitHubClient
from hub.app.store import HubSession, HubStore, HubUser

SESSION_COOKIE = "hub_session"
OAUTH_STATE_COOKIE = "hub_oauth_state"
OAUTH_REDIRECT_COOKIE = "hub_oauth_redirect"
SESSION_MAX_AGE = 60 * 60 * 24 * 14


def oauth_callback_url(request: Request, config: HubConfig) -> str:
    """Match redirect_uri to the host the user actually opened in the browser."""
    host = (request.headers.get("host") or "").strip()
    if host:
        scheme = request.url.scheme or "http"
        if host.startswith("127.0.0.1") or host.startswith("localhost"):
            return f"{scheme}://{host}/auth/callback"
    if config.public_url:
        return config.public_url.rstrip("/") + "/auth/callback"
    return str(request.base_url).rstrip("/") + "/auth/callback"


def _serializer(config: HubConfig) -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(config.session_secret, salt="hub-session")


def oauth_login_url(config: HubConfig, *, redirect_uri: str) -> tuple[str, str]:
    if not config.github_client_id:
        raise HTTPException(503, "GitHub OAuth is not configured")
    state = secrets.token_urlsafe(24)
    params = urlencode(
        {
            "client_id": config.github_client_id,
            "redirect_uri": redirect_uri,
            "scope": "read:user repo",
            "state": state,
        }
    )
    return f"https://github.com/login/oauth/authorize?{params}", state


async def oauth_callback(
    *,
    config: HubConfig,
    store: HubStore,
    code: str,
    state: str,
    expected_state: Optional[str],
    redirect_uri: str,
) -> HubSession:
    if not expected_state or state != expected_state:
        raise HTTPException(400, "Invalid OAuth state")
    if not config.github_client_secret:
        raise HTTPException(503, "GitHub OAuth is not configured")

    try:
        token_r = await github_request(
            "POST",
            "https://github.com/login/oauth/access_token",
            headers={"Accept": "application/json"},
            data={
                "client_id": config.github_client_id,
                "client_secret": config.github_client_secret,
                "code": code,
                "redirect_uri": redirect_uri,
            },
        )
    except httpx.HTTPError as exc:
        raise HTTPException(502, f"GitHub token exchange failed: {exc}") from exc
    token_r.raise_for_status()
    token_data = token_r.json()
    access_token = token_data.get("access_token")
    if not access_token:
        raise HTTPException(400, "GitHub did not return an access token")

    gh = GitHubClient(access_token)
    profile = await gh.get_user()
    github_id = int(profile["id"])
    user = store.get_user(github_id)
    if user is None:
        user = HubUser(
            github_id=github_id,
            login=str(profile.get("login") or ""),
            avatar_url=str(profile.get("avatar_url") or ""),
        )
    else:
        user.login = str(profile.get("login") or user.login)
        user.avatar_url = str(profile.get("avatar_url") or user.avatar_url)
    store.save_user(user)
    return store.create_session(github_id, access_token)


def set_session_cookie(response: Response, config: HubConfig, session_id: str) -> None:
    token = _serializer(config).dumps({"sid": session_id})
    response.set_cookie(
        SESSION_COOKIE,
        token,
        httponly=True,
        secure=config.public_url.startswith("https"),
        samesite="lax",
        max_age=SESSION_MAX_AGE,
    )


def clear_session_cookie(response: Response) -> None:
    response.delete_cookie(SESSION_COOKIE)


def get_session(request: Request, config: HubConfig, store: HubStore) -> Optional[HubSession]:
    raw = request.cookies.get(SESSION_COOKIE)
    if not raw:
        return None
    try:
        data = _serializer(config).loads(raw, max_age=SESSION_MAX_AGE)
    except (BadSignature, SignatureExpired):
        return None
    sid = data.get("sid") if isinstance(data, dict) else None
    if not sid:
        return None
    return store.get_session(str(sid))


def require_session(request: Request, config: HubConfig, store: HubStore) -> HubSession:
    session = get_session(request, config, store)
    if session is None:
        raise HTTPException(401, "Sign in required")
    return session
