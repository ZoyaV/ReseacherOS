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


def test_analysis_facade_reexports_specialized_implementations() -> None:
    analysis = import_module("koi.review.analysis")

    assert analysis._extract_json_object is import_module("koi.review.parsing")._extract_json_object
    assert analysis.propose_clusters is import_module("koi.review.clustering").propose_clusters
    assert analysis.summarize_paper is import_module("koi.review.summaries").summarize_paper
    assert analysis.build_cluster_report is import_module("koi.review.rendering").build_cluster_report
    assert (
        analysis.prepare_related_work_material
        is import_module("koi.review.related_work").prepare_related_work_material
    )
