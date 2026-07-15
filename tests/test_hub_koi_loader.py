"""Tests for ResearchOS Hub."""

from __future__ import annotations

import json
from pathlib import Path

from hub.app.koi_loader import load_project_from_koi_root, project_snapshot


def test_load_talkingheads_snapshot_if_present():
    root = Path(__file__).resolve().parents[3] / "TalkingHeads" / "koi-structure"
    if not (root / "project.md").exists():
        return
    project = load_project_from_koi_root(root)
    assert project is not None
    assert project.title
    snap = project_snapshot(root)
    assert snap is not None
    assert "nodes" in snap
    assert "boards" in snap
