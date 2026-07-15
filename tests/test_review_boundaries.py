"""Import and compatibility contracts for the paper-review capability."""

from importlib import import_module


def test_review_api_uses_canonical_capability() -> None:
    assert import_module("api.routers.review").router.prefix == ""
    assert callable(import_module("koi.review.pipeline").run_review_agent)


def test_review_package_import_remains_compatible() -> None:
    assert import_module("koi.services.review") is import_module("koi.review")


def test_review_agent_import_remains_compatible() -> None:
    assert import_module("koi.services.review_agent") is import_module("koi.review")


def test_review_submodule_import_remains_compatible() -> None:
    assert import_module("koi.services.review.analysis") is import_module("koi.review.analysis")
