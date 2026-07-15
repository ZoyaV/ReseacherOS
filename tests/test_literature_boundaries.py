"""Boundary contracts for the literature capability."""

from importlib import import_module

from koi.literature.naming import safe_filename, slugify


def test_literature_naming_contract() -> None:
    assert slugify("  Scene_Graph: Review!  ") == "scene-graph-review"
    assert safe_filename('A <paper>: "result"') == "A_paper_result.md"


def test_service_import_remains_compatible() -> None:
    legacy = import_module("koi.services.literature")
    implementation = import_module("koi.literature")

    assert legacy is implementation


def test_literature_api_and_review_pipeline_import() -> None:
    assert import_module("api.routers.library").router.prefix == ""
    assert callable(import_module("koi.review.pipeline").run_review_agent)
