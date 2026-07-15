"""Project visibility helpers for Hub."""

from __future__ import annotations

from typing import Optional

from hub.app.store import HubProject, HubStore


def can_view_project_with_store(
    project: HubProject, viewer_github_id: Optional[int], store: HubStore
) -> bool:
    if not project.enabled and viewer_github_id != project.owner_github_id:
        return False
    if project.visibility == "public":
        return True
    if project.visibility == "unlisted":
        return False
    if project.visibility == "network" and viewer_github_id is not None:
        if viewer_github_id == project.owner_github_id:
            return True
        return project.owner_github_id in store.following_ids(viewer_github_id)
    return False


def is_project_listed(project: HubProject) -> bool:
    """Shown in Explore / network feeds (not direct owner preview)."""
    return bool(project.enabled)
