"""Hub project identity: one listing per repo branch."""

from __future__ import annotations

from typing import Iterable

from hub.app.store import HubProject, HubStore


def source_key(repo_full_name: str, branch: str) -> tuple[str, str]:
    return repo_full_name.strip().lower(), branch.strip().lower()


def project_rank(project: HubProject) -> tuple[int, str, str]:
    """Higher is better when picking the canonical registration."""
    return (
        1 if project.enabled else 0,
        project.last_sync_at or "",
        project.created_at or "",
    )


def pick_canonical(projects: Iterable[HubProject]) -> HubProject:
    return max(projects, key=project_rank)


def dedupe_hub_projects(projects: Iterable[HubProject]) -> list[HubProject]:
    by_source: dict[tuple[str, str], list[HubProject]] = {}
    for project in projects:
        key = source_key(project.repo_full_name, project.branch)
        by_source.setdefault(key, []).append(project)
    canonical = [pick_canonical(group) for group in by_source.values()]
    canonical.sort(key=lambda p: p.title.lower())
    return canonical


def find_project_by_source(
    store: HubStore,
    owner_github_id: int,
    repo_full_name: str,
    branch: str,
) -> HubProject | None:
    key = source_key(repo_full_name, branch)
    matches = [
        p
        for p in store.list_projects()
        if p.owner_github_id == owner_github_id
        and source_key(p.repo_full_name, p.branch) == key
    ]
    if not matches:
        return None
    return pick_canonical(matches)


def find_canonical_slug(store: HubStore, hub_project: HubProject) -> str:
    key = source_key(hub_project.repo_full_name, hub_project.branch)
    matches = [
        p
        for p in store.list_projects()
        if source_key(p.repo_full_name, p.branch) == key
    ]
    if not matches:
        return hub_project.slug
    return pick_canonical(matches).slug
