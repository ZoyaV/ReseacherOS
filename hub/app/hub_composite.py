"""Composite (merged) hypothesis trees for Hub snapshots."""

from __future__ import annotations

import re
import unicodedata
from typing import Any, Optional

from hub.app.client_project import project_from_client
from hub.app.store import HubProject, HubStore
from koi.services.composite import build_composite, composite_to_client

AUTO_COMPOSITE_PREFIX = "auto-problem:"


def _normalize_title(value: str) -> str:
    text = unicodedata.normalize("NFKC", value or "").strip().lower()
    text = re.sub(r"\s+", " ", text)
    return text


def _problem_title(project: dict[str, Any]) -> Optional[str]:
    for node in project.get("nodes") or []:
        if node.get("node_type") == "problem":
            title = str(node.get("title") or "").strip()
            if title:
                return title
    return None


def _problem_key(project: dict[str, Any]) -> Optional[str]:
    title = _problem_title(project)
    if not title:
        return None
    normalized = _normalize_title(title)
    return normalized or None


def _auto_composite_id(problem_key: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", problem_key).strip("-")[:48] or "problem"
    return f"{AUTO_COMPOSITE_PREFIX}{slug}"


def _composite_key(hub_project: HubProject, project: dict[str, Any]) -> Optional[str]:
    explicit = (hub_project.composite_id or "").strip()
    if explicit:
        return explicit
    problem = _problem_key(project)
    if problem:
        return _auto_composite_id(problem)
    return None


def list_hub_composites(
    members: list[tuple[HubProject, dict[str, Any]]],
) -> list[dict[str, Any]]:
    groups: dict[str, list[tuple[HubProject, dict[str, Any]]]] = {}
    for hub_project, project in members:
        key = _composite_key(hub_project, project)
        if not key:
            continue
        groups.setdefault(key, []).append((hub_project, project))

    summaries: list[dict[str, Any]] = []
    for composite_id, group in groups.items():
        if len(group) < 2:
            continue
        member_ids = [project["id"] for _, project in group if project.get("id")]
        if len(set(member_ids)) < 2:
            continue
        title = _problem_title(group[0][1]) or group[0][0].title or composite_id
        summaries.append(
            {
                "id": composite_id,
                "title": title,
                "member_ids": member_ids,
                "programs": [],
                "auto": composite_id.startswith(AUTO_COMPOSITE_PREFIX),
            }
        )
    summaries.sort(key=lambda item: str(item.get("title") or ""))
    return summaries


def load_hub_composite(
    store: HubStore,
    composite_id: str,
    members: list[tuple[HubProject, dict[str, Any]]],
) -> Optional[dict[str, Any]]:
    grouped: list[tuple[str, Any]] = []
    for hub_project, project in members:
        key = _composite_key(hub_project, project)
        if key != composite_id:
            continue
        grouped.append((str(project.get("id") or hub_project.slug), project_from_client(project)))
    if len(grouped) < 2:
        return None
    composite = build_composite(composite_id, grouped)
    if composite is None:
        return None
    return composite_to_client(composite)
