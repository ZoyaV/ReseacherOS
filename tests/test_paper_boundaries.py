"""Import and compatibility contracts for the paper capability."""

from importlib import import_module
import runpy
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    ("legacy", "canonical"),
    (
        ("koi.services.paper_catalog", "koi.paper.catalog"),
        ("koi.services.paper_comments", "koi.paper.comments"),
        ("koi.services.paper_generator", "koi.paper.generator"),
        ("koi.services.paper_inbox", "koi.paper.inbox"),
        ("koi.services.paper_page_counts", "koi.paper.page_counts"),
        ("koi.services.paper_runner", "koi.paper.runner"),
    ),
)
def test_service_imports_remain_compatible(legacy: str, canonical: str) -> None:
    assert import_module(legacy) is import_module(canonical)


@pytest.mark.parametrize(
    "relative_path",
    ("scripts/koi_paper.py", "scripts/koi_paper_inbox.py"),
)
def test_paper_cli_imports(relative_path: str) -> None:
    namespace = runpy.run_path(str(ROOT / relative_path), run_name="paper_smoke")

    assert callable(namespace["main"])
