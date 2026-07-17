"""Tests for tree/ + code project install / migrate."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from koi.adapters import project_mount as pm
from koi.adapters.project_install import (
    InstallCase,
    classify_install,
    install_project,
    layout_status,
)
from koi.adapters.workspace import reset_workspace_cache


def _git(cwd: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True)


def _init_remote_repo(path: Path) -> None:
    path.mkdir(parents=True)
    _git(path, "init", "--bare", "-b", "main")


@pytest.fixture
def workspace(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    engine = tmp_path / "ReseachOS"
    engine.mkdir()
    monkeypatch.setattr(pm, "ENGINE_ROOT", engine)
    monkeypatch.setenv("KOI_SCAN_ROOTS", str(tmp_path))
    reset_workspace_cache()
    pm.rescan_projects()
    yield tmp_path
    reset_workspace_cache()


def test_classify_new_empty(workspace: Path):
    plan = classify_install("fresh_idea", scan_root=workspace, create_if_missing=True)
    assert plan.case == InstallCase.NEW_EMPTY


def test_install_new_empty(workspace: Path):
    result = install_project("fresh_idea", scan_root=workspace, create_if_missing=True)
    assert result["ok"] is True
    assert result["case"] == "new_empty"
    assert (workspace / "fresh_idea" / "projectcode" / "README.md").is_file()
    assert (workspace / "tree" / "fresh_idea" / "koi-structure" / "project.md").is_file()
    pm.rescan_projects()
    mount = pm.get_mount("fresh-idea")
    assert mount is not None
    assert pm.is_under_tree(mount.koi_root)


def test_classify_and_install_integrated(workspace: Path):
    remote = workspace / "remote.git"
    _init_remote_repo(remote)
    repo = workspace / "TalkingHeads"
    repo.mkdir()
    (repo / "main.py").write_text("print('hi')\n", encoding="utf-8")
    _git(repo, "init", "-b", "main")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "code")
    _git(repo, "remote", "add", "origin", str(remote))
    _git(repo, "push", "-u", "origin", "main")

    # orphan sync branch with koi-structure
    bootstrap = workspace / "_bootstrap"
    _git(repo, "worktree", "add", "-b", "koi/research", "--orphan", str(bootstrap))
    koi = bootstrap / "koi-structure"
    koi.mkdir()
    (koi / "project.md").write_text(
        "---\nid: talking-heads\ntitle: TalkingHeads\ngit_repo: true\n"
        "git_sync_branch: koi/research\n---\n\n# problem: p\n\nx\n",
        encoding="utf-8",
    )
    _git(bootstrap, "add", "koi-structure")
    _git(bootstrap, "commit", "-m", "init koi")
    _git(bootstrap, "push", "-u", "origin", "koi/research")
    _git(repo, "worktree", "remove", "--force", str(bootstrap))

    plan = classify_install(repo, scan_root=workspace)
    assert plan.case == InstallCase.INTEGRATED

    result = install_project(repo, scan_root=workspace, push=False)
    assert result["ok"] is True
    assert (workspace / "tree" / "TalkingHeads" / "koi-structure" / "project.md").is_file()
    assert (workspace / "tree" / "TalkingHeads" / ".git").exists()
    pm.rescan_projects()
    mount = pm.get_mount("talking-heads")
    assert mount is not None
    assert mount.repo_root == repo.resolve()
    assert pm.is_under_tree(mount.koi_root)


def test_migrate_legacy_in_repo_koi(workspace: Path):
    remote = workspace / "remote.git"
    _init_remote_repo(remote)
    repo = workspace / "verl_agent"
    koi = repo / "koi-structure"
    koi.mkdir(parents=True)
    (koi / "project.md").write_text(
        "---\nid: verl-agent\ntitle: Verl\ngit_repo: true\n"
        "git_sync_branch: koi/research\n---\n\n# problem: p\n\nx\n",
        encoding="utf-8",
    )
    (repo / "train.py").write_text("pass\n", encoding="utf-8")
    _git(repo, "init", "-b", "feature")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "code+koi")
    _git(repo, "remote", "add", "origin", str(remote))
    _git(repo, "push", "-u", "origin", "feature")

    plan = classify_install(repo, scan_root=workspace)
    assert plan.case == InstallCase.MIGRATE_TO_TREE

    result = install_project(repo, scan_root=workspace, push=True)
    assert result["ok"] is True
    assert (workspace / "tree" / "verl_agent" / "koi-structure" / "project.md").is_file()
    pm.rescan_projects()
    mount = pm.get_mount("verl-agent")
    assert mount is not None
    assert pm.is_under_tree(mount.koi_root)


def test_layout_status(workspace: Path):
    install_project("alpha", scan_root=workspace, create_if_missing=True)
    status = layout_status(scan_root=workspace)
    names = {p["name"] for p in status["projects"]}
    assert "alpha" in names
    alpha = next(p for p in status["projects"] if p["name"] == "alpha")
    assert alpha["tree_koi"] is True
    assert alpha["case"] == "already_ok"
