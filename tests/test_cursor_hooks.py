"""Import-smoke checks for Cursor hooks without executing their main functions."""

import runpy
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
CONTENT_SKILLS = (
    "koi-agent-chat",
    "koi-done-research",
    "koi-execute-card",
    "koi-knowledge-curator",
    "koi-paper",
    "koi-project-sync",
    "koi-prose-style",
    "koi-related-work",
    "koi-report-review",
)


@pytest.mark.parametrize(
    "relative_path",
    (
        ".cursor/hooks/koi-agent-chat-hook.py",
        ".cursor/hooks/koi-done-research-hook.py",
        ".cursor/hooks/koi-project-sync-hook.py",
    ),
)
def test_cursor_hook_imports(relative_path: str) -> None:
    namespace = runpy.run_path(str(ROOT / relative_path), run_name="cursor_hook_smoke")

    assert callable(namespace["main"])


@pytest.mark.parametrize("skill_name", CONTENT_SKILLS)
def test_cursor_content_skill_links_to_canonical_skill(skill_name: str) -> None:
    cursor_skill = ROOT / ".cursor" / "skills" / skill_name
    canonical_skill = ROOT / "agents" / "skills" / skill_name

    assert cursor_skill.is_symlink()
    assert cursor_skill.resolve() == canonical_skill.resolve()
    assert (cursor_skill / "SKILL.md").is_file()


def test_report_skill_owns_its_templates() -> None:
    skill = ROOT / "agents" / "skills" / "koi-report-review"

    for name in ("experiment-report.md", "report-rules.md", "report-skeleton.md"):
        assert (skill / name).is_file()
