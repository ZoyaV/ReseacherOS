"""Hub runtime configuration from environment."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _env(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


@dataclass(frozen=True)
class HubConfig:
    public_url: str
    github_client_id: str
    github_client_secret: str
    session_secret: str
    data_dir: Path
    s3_bucket: str
    s3_endpoint: str
    s3_access_key: str
    s3_secret_key: str
    default_branch: str
    koi_path: str

    @property
    def oauth_callback(self) -> str:
        base = self.public_url.rstrip("/")
        return f"{base}/auth/callback"

    @property
    def use_s3(self) -> bool:
        return bool(self.s3_bucket and self.s3_access_key and self.s3_secret_key)

    @classmethod
    def from_env(cls) -> HubConfig:
        hub_root = Path(__file__).resolve().parents[1]
        data_dir = Path(_env("HUB_DATA_DIR", str(hub_root / ".data")))
        return cls(
            public_url=_env("HUB_PUBLIC_URL", "http://127.0.0.1:8020"),
            github_client_id=_env("GITHUB_CLIENT_ID"),
            github_client_secret=_env("GITHUB_CLIENT_SECRET"),
            session_secret=_env("HUB_SESSION_SECRET", "dev-change-me"),
            data_dir=data_dir,
            s3_bucket=_env("HUB_S3_BUCKET"),
            s3_endpoint=_env("HUB_S3_ENDPOINT", "https://storage.yandexcloud.net"),
            s3_access_key=_env("HUB_S3_ACCESS_KEY"),
            s3_secret_key=_env("HUB_S3_SECRET_KEY"),
            default_branch=_env("HUB_DEFAULT_BRANCH", "koi/research"),
            koi_path=_env("HUB_KOI_PATH", "koi-structure"),
        )
