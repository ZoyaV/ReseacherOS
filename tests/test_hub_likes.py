"""Hub project likes: store toggle + catalog fields."""

from __future__ import annotations

from types import SimpleNamespace

from hub.app.config import HubConfig
from hub.app.main import _catalog_project_item
from hub.app.store import HubStore


def _local_store(tmp_path) -> HubStore:
    return HubStore(
        HubConfig(
            public_url="http://localhost",
            github_client_id="",
            github_client_secret="",
            session_secret="test",
            data_dir=tmp_path,
            s3_bucket="",
            s3_endpoint="",
            s3_access_key="",
            s3_secret_key="",
            default_branch="koi/research",
            koi_path="koi-structure",
        )
    )


def test_toggle_like_add_and_remove(tmp_path):
    store = _local_store(tmp_path)
    assert store.get_likes("demo") == {
        "user_ids": [],
        "updated_at": "",
        "count": 0,
    }

    first = store.toggle_like(42, "demo")
    assert first == {"liked": True, "count": 1}
    likes = store.get_likes("demo")
    assert likes["user_ids"] == [42]
    assert likes["count"] == 1
    assert likes["updated_at"]

    second = store.toggle_like(42, "demo")
    assert second == {"liked": False, "count": 0}
    assert store.get_likes("demo")["user_ids"] == []

    store.toggle_like(7, "demo")
    store.toggle_like(42, "demo")
    assert store.get_likes("demo")["user_ids"] == [7, 42]
    assert store.get_likes("demo")["count"] == 2


def test_catalog_item_includes_like_fields(monkeypatch, tmp_path):
    store = _local_store(tmp_path)
    store.toggle_like(99, "proj")
    monkeypatch.setattr("hub.app.main.store", store)

    project = SimpleNamespace(
        slug="proj",
        title="Proj",
        owner_login="alice",
        owner_github_id=1,
        repo_full_name="alice/proj",
        branch="koi/research",
        visibility="public",
        last_sync_at="2026-01-01T00:00:00+00:00",
        secret_token="",
    )
    item = _catalog_project_item(
        project,
        {"project": {"nodes": [1, 2]}},
        viewer_id=99,
        following=set(),
    )
    assert item["like_count"] == 1
    assert item["liked_by_me"] is True

    item_other = _catalog_project_item(
        project,
        None,
        viewer_id=5,
        following=set(),
    )
    assert item_other["like_count"] == 1
    assert item_other["liked_by_me"] is False
