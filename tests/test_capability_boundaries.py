"""Canonical and compatibility imports for remaining extracted capabilities."""

from importlib import import_module
import runpy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_cursor_service_imports_remain_compatible() -> None:
    assert import_module("koi.services.cursor_app") is import_module("koi.cursor.app")
    assert import_module("koi.services.cursor_usage") is import_module("koi.cursor.usage")


def test_related_work_service_imports_remain_compatible() -> None:
    assert import_module("koi.services.related_work") is import_module("koi.related_work.service")
    assert import_module("koi.services.related_work_inbox") is import_module("koi.related_work.inbox")


def test_cursor_and_review_api_imports() -> None:
    assert import_module("api.routers.cursor").router.prefix == ""
    assert import_module("api.routers.review").router.prefix == ""


def test_related_work_cli_imports() -> None:
    for relative_path in ("scripts/koi_related_work.py", "scripts/koi_related_work_inbox.py"):
        namespace = runpy.run_path(str(ROOT / relative_path), run_name="capability_smoke")
        assert callable(namespace["main"])
