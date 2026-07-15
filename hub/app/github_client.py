"""GitHub API helpers — fetch koi-structure only."""

from __future__ import annotations

import base64
import shutil
import tarfile
import io
from pathlib import Path
from typing import Any, Optional
from urllib.parse import quote

import httpx


from hub.app.github_http import github_http_client, github_request


class GitHubClient:
    API = "https://api.github.com"

    def __init__(self, access_token: str) -> None:
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    async def get_user(self) -> dict[str, Any]:
        r = await github_request("GET", f"{self.API}/user", headers=self.headers)
        r.raise_for_status()
        return r.json()

    async def list_repos(self, *, page: int = 1, per_page: int = 100) -> list[dict[str, Any]]:
        async with github_http_client() as client:
            r = await client.get(
                f"{self.API}/user/repos",
                headers=self.headers,
                params={
                    "sort": "updated",
                    "per_page": per_page,
                    "page": page,
                    "affiliation": "owner,collaborator,organization_member",
                },
            )
            r.raise_for_status()
            data = r.json()
            return data if isinstance(data, list) else []

    async def branch_exists(self, repo_full_name: str, branch: str) -> bool:
        owner, name = repo_full_name.split("/", 1)
        branch_path = quote(branch, safe="")
        r = await github_request(
            "GET",
            f"{self.API}/repos/{owner}/{name}/branches/{branch_path}",
            headers=self.headers,
        )
        return r.status_code == 200

    async def fetch_koi_structure(
        self,
        repo_full_name: str,
        branch: str,
        koi_path: str,
        dest: Path,
    ) -> Optional[str]:
        """Download koi-structure tree; return HEAD commit sha if found."""
        owner, name = repo_full_name.split("/", 1)
        if dest.exists():
            shutil.rmtree(dest)
        dest.mkdir(parents=True, exist_ok=True)

        commit_sha = await self._resolve_commit(owner, name, branch)
        tarball_sha = await self._fetch_via_tarball(owner, name, branch, koi_path, dest)
        if tarball_sha:
            return commit_sha or tarball_sha

        async with github_http_client(timeout=120.0, follow_redirects=True) as client:
            if commit_sha:
                ok = await self._fetch_tree(client, owner, name, commit_sha, koi_path, dest)
                if ok:
                    return commit_sha
        return None

    async def _resolve_commit(self, owner: str, name: str, branch: str) -> str:
        branch_path = quote(branch, safe="")
        r = await github_request(
            "GET",
            f"{self.API}/repos/{owner}/{name}/branches/{branch_path}",
            headers=self.headers,
        )
        if r.status_code != 200:
            return ""
        data = r.json()
        commit = data.get("commit") or {}
        return str(commit.get("sha") or "")

    async def _fetch_tree(
        self,
        client: httpx.AsyncClient,
        owner: str,
        name: str,
        commit_sha: str,
        koi_path: str,
        dest: Path,
    ) -> bool:
        tree_r = await client.get(
            f"{self.API}/repos/{owner}/{name}/git/trees/{commit_sha}",
            headers=self.headers,
            params={"recursive": "1"},
        )
        if tree_r.status_code != 200:
            return False
        prefix = koi_path.strip("/") + "/"
        entries = tree_r.json().get("tree") or []
        blobs = [
            e
            for e in entries
            if e.get("type") == "blob" and str(e.get("path", "")).startswith(prefix)
        ]
        if not blobs:
            return False
        for entry in blobs:
            rel = str(entry["path"])[len(prefix) :]
            if not rel:
                continue
            blob_sha = entry.get("sha")
            if not blob_sha:
                continue
            blob_r = await client.get(
                f"{self.API}/repos/{owner}/{name}/git/blobs/{blob_sha}",
                headers=self.headers,
            )
            if blob_r.status_code != 200:
                continue
            payload = blob_r.json()
            content = payload.get("content") or ""
            encoding = payload.get("encoding")
            if encoding == "base64":
                raw = base64.b64decode(content)
            else:
                raw = str(content).encode("utf-8")
            out = dest / rel
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(raw)
        return (dest / "project.md").exists()

    async def _fetch_via_tarball(
        self,
        owner: str,
        name: str,
        branch: str,
        koi_path: str,
        dest: Path,
    ) -> Optional[str]:
        branch_path = quote(branch, safe="")
        r = await github_request(
            "GET",
            f"{self.API}/repos/{owner}/{name}/tarball/{branch_path}",
            headers={**self.headers, "Accept": "application/vnd.github+json"},
            follow_redirects=True,
            timeout=120.0,
        )
        if r.status_code != 200:
            return None
        prefix = koi_path.strip("/") + "/"
        with tarfile.open(fileobj=io.BytesIO(r.content), mode="r:gz") as tar:
            for member in tar.getmembers():
                if not member.isfile():
                    continue
                parts = member.name.split("/", 1)
                if len(parts) != 2:
                    continue
                rel_path = parts[1]
                if not rel_path.startswith(prefix):
                    continue
                out_rel = rel_path[len(prefix) :]
                if not out_rel:
                    continue
                extracted = tar.extractfile(member)
                if extracted is None:
                    continue
                out = dest / out_rel
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_bytes(extracted.read())
        if not (dest / "project.md").exists():
            return None
        return "tarball"
