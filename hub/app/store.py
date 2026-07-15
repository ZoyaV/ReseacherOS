"""Persistence for users, projects, sessions, and snapshots."""

from __future__ import annotations

import json
import secrets
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from hub.app.config import HubConfig


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class HubUser:
    github_id: int
    login: str
    avatar_url: str = ""
    discoverable: bool = True
    created_at: str = field(default_factory=_utcnow)


@dataclass
class HubProject:
    slug: str
    owner_github_id: int
    owner_login: str
    repo_full_name: str
    branch: str
    title: str
    visibility: str  # public | network | unlisted
    secret_token: str = ""
    composite_id: str = ""
    enabled: bool = True
    last_sync_at: str = ""
    last_commit: str = ""
    created_at: str = field(default_factory=_utcnow)


def parse_hub_project(raw: dict) -> HubProject:
    data = dict(raw)
    data.setdefault("enabled", True)
    data.setdefault("composite_id", "")
    return HubProject(**data)


@dataclass
class HubSession:
    session_id: str
    github_id: int
    access_token: str
    created_at: str = field(default_factory=_utcnow)


class HubStore:
    def __init__(self, config: HubConfig) -> None:
        self.config = config
        self._s3 = None
        if config.use_s3:
            import boto3

            self._s3 = boto3.client(
                "s3",
                endpoint_url=config.s3_endpoint,
                aws_access_key_id=config.s3_access_key,
                aws_secret_access_key=config.s3_secret_key,
            )
        else:
            config.data_dir.mkdir(parents=True, exist_ok=True)

    def _key(self, *parts: str) -> str:
        return "/".join(parts)

    def _read_json(self, key: str) -> Any:
        if self._s3:
            try:
                obj = self._s3.get_object(Bucket=self.config.s3_bucket, Key=key)
                return json.loads(obj["Body"].read().decode("utf-8"))
            except Exception as exc:
                code = getattr(getattr(exc, "response", None), "get", lambda *_: {})("Error", {}).get("Code")
                if code in {"NoSuchKey", "404"}:
                    return None
                return None
        path = self.config.data_dir / key
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def _write_json(self, key: str, data: Any) -> None:
        body = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
        if self._s3:
            self._s3.put_object(
                Bucket=self.config.s3_bucket,
                Key=key,
                Body=body.encode("utf-8"),
                ContentType="application/json",
            )
            return
        path = self.config.data_dir / key
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")

    def list_users(self) -> list[HubUser]:
        index = self._read_json("users/index.json") or []
        users: list[HubUser] = []
        for github_id in index:
            raw = self._read_json(f"users/{github_id}.json")
            if raw:
                users.append(HubUser(**raw))
        return users

    def get_user(self, github_id: int) -> Optional[HubUser]:
        raw = self._read_json(f"users/{github_id}.json")
        return HubUser(**raw) if raw else None

    def save_user(self, user: HubUser) -> None:
        self._write_json(f"users/{user.github_id}.json", asdict(user))
        index = self._read_json("users/index.json") or []
        sid = str(user.github_id)
        if sid not in index:
            index.append(sid)
            self._write_json("users/index.json", index)

    def list_projects(self) -> list[HubProject]:
        index = self._read_json("projects/index.json") or []
        out: list[HubProject] = []
        for slug in index:
            raw = self._read_json(f"projects/{slug}.json")
            if raw:
                out.append(parse_hub_project(raw))
        return out

    def get_project(self, slug: str) -> Optional[HubProject]:
        raw = self._read_json(f"projects/{slug}.json")
        return parse_hub_project(raw) if raw else None

    def save_project(self, project: HubProject) -> None:
        self._write_json(f"projects/{project.slug}.json", asdict(project))
        index = self._read_json("projects/index.json") or []
        if project.slug not in index:
            index.append(project.slug)
            self._write_json("projects/index.json", index)

    def delete_project(self, slug: str) -> None:
        if self._s3:
            self._s3.delete_object(Bucket=self.config.s3_bucket, Key=f"projects/{slug}.json")
            self._s3.delete_object(Bucket=self.config.s3_bucket, Key=f"snapshots/{slug}.json")
        else:
            project_path = self.config.data_dir / "projects" / f"{slug}.json"
            snapshot_path = self.config.data_dir / "snapshots" / f"{slug}.json"
            if project_path.exists():
                project_path.unlink()
            if snapshot_path.exists():
                snapshot_path.unlink()
        index = self._read_json("projects/index.json") or []
        if slug in index:
            index = [s for s in index if s != slug]
            self._write_json("projects/index.json", index)

    def save_snapshot(self, slug: str, payload: dict[str, Any]) -> None:
        self._write_json(f"snapshots/{slug}.json", payload)

    def get_snapshot(self, slug: str) -> Optional[dict[str, Any]]:
        return self._read_json(f"snapshots/{slug}.json")

    def create_session(self, github_id: int, access_token: str) -> HubSession:
        session = HubSession(
            session_id=secrets.token_urlsafe(32),
            github_id=github_id,
            access_token=access_token,
        )
        self._write_json(f"sessions/{session.session_id}.json", asdict(session))
        return session

    def get_session(self, session_id: str) -> Optional[HubSession]:
        raw = self._read_json(f"sessions/{session_id}.json")
        return HubSession(**raw) if raw else None

    def delete_session(self, session_id: str) -> None:
        if self._s3:
            self._s3.delete_object(
                Bucket=self.config.s3_bucket,
                Key=self._key("sessions", f"{session_id}.json"),
            )
            return
        path = self.config.data_dir / "sessions" / f"{session_id}.json"
        if path.exists():
            path.unlink()

    def list_follows(self) -> list[dict[str, int]]:
        return self._read_json("social/follows.json") or []

    def add_follow(self, follower_id: int, following_id: int) -> None:
        rows = self.list_follows()
        if any(r["follower_id"] == follower_id and r["following_id"] == following_id for r in rows):
            return
        rows.append({"follower_id": follower_id, "following_id": following_id})
        self._write_json("social/follows.json", rows)

    def following_ids(self, follower_id: int) -> set[int]:
        return {r["following_id"] for r in self.list_follows() if r["follower_id"] == follower_id}

    def list_bookmarks(self) -> list[dict[str, Any]]:
        return self._read_json("social/bookmarks.json") or []

    def user_bookmarks(self, user_id: int) -> list[dict[str, str]]:
        return [
            {"slug": str(r["slug"]), "token": str(r.get("token") or "")}
            for r in self.list_bookmarks()
            if r.get("user_id") == user_id
        ]

    def add_bookmark(self, user_id: int, slug: str, token: str = "") -> bool:
        rows = self.list_bookmarks()
        for row in rows:
            if row.get("user_id") == user_id and row.get("slug") == slug:
                if token and row.get("token") != token:
                    row["token"] = token
                    self._write_json("social/bookmarks.json", rows)
                return False
        rows.append(
            {
                "user_id": user_id,
                "slug": slug,
                "token": token or "",
                "created_at": _utcnow(),
            }
        )
        self._write_json("social/bookmarks.json", rows)
        return True

    def remove_bookmark(self, user_id: int, slug: str) -> None:
        rows = [
            r
            for r in self.list_bookmarks()
            if not (r.get("user_id") == user_id and r.get("slug") == slug)
        ]
        self._write_json("social/bookmarks.json", rows)

    @staticmethod
    def new_slug(title: str, repo_full_name: str) -> str:
        base = title.lower().strip() or repo_full_name.split("/")[-1]
        cleaned = "".join(ch if ch.isalnum() else "-" for ch in base).strip("-")
        cleaned = "-".join(part for part in cleaned.split("-") if part)[:40] or "project"
        suffix = uuid.uuid4().hex[:6]
        return f"{cleaned}-{suffix}"

    @staticmethod
    def new_secret() -> str:
        return secrets.token_urlsafe(18)
