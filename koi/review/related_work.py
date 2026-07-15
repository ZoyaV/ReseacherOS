from __future__ import annotations

from koi.adapters.agent_backends import run_agent
from koi.adapters.workspace import get_workspace
from koi.review.clustering import _parse_paper_answer_clusters
from koi.review.models import PaperAnswerArtifact, PaperAnswerCluster
from koi.review.parsing import _quote_excerpt, _strip_code_fences
from koi.review.storage import load_latest_paper_answer_run

def _build_related_works_prompt(
    *,
    project_id: str,
    question: str,
    problem: str,
    clusters: list[PaperAnswerCluster],
    artifacts: list[PaperAnswerArtifact],
) -> str:
    artifact_by_title = {artifact.title: artifact for artifact in artifacts}
    cluster_blocks: list[str] = []
    for cluster in clusters:
        lines = [
            f"Cluster: {cluster.label}",
            f"Shared answer: {cluster.answer}",
            f"Why this cluster exists: {cluster.rationale}",
            f"How it differs: {cluster.distinguishing_features}",
            f"Signature terms: {', '.join(cluster.signature_terms) if cluster.signature_terms else 'n/a'}",
            "Papers:",
        ]
        for title in cluster.paper_titles:
            artifact = artifact_by_title.get(title)
            if artifact is None:
                continue
            year = f" ({artifact.year})" if artifact.year is not None else ""
            lines.append(f"- {artifact.title}{year}")
            lines.append(f"  Short answer: {artifact.short_answer}")
            lines.append(f"  Detailed answer: {artifact.comprehensive_answer}")
            if artifact.evidence:
                lines.append(
                    f"  Evidence: {' | '.join(_quote_excerpt(snippet, limit=220) for snippet in artifact.evidence[:2])}"
                )
            lines.append(f"  Limitations: {artifact.limitations}")
        cluster_blocks.append("\n".join(lines))

    return (
        "You are writing the Related Works section for a research paper.\n\n"
        "Return markdown only, with no code fences.\n"
        "Write a concise but substantive section that synthesizes the selected literature clusters into a coherent narrative.\n"
        "Do not merely list papers one by one. Merge nearby clusters when helpful and explicitly compare their assumptions, representations, and limitations.\n"
        "Ground every claim only in the provided cluster and paper summaries.\n"
        "Prefer citation-style mentions by paper title in prose.\n"
        "Structure requirements:\n"
        "- Start with the heading `## Related Works`.\n"
        "- Write 2-5 paragraphs.\n"
        "- The first paragraph should frame the literature relative to the target problem.\n"
        "- Middle paragraphs should synthesize the selected clusters, including similarities and differences.\n"
        "- End with a brief gap statement explaining what remains unresolved for this problem.\n"
        "- Avoid bullet lists unless absolutely necessary.\n\n"
        f"Project id: {project_id}\n"
        f"Original paper-question prompt: {question or 'n/a'}\n"
        f"Target problem for the paper: {problem.strip()}\n\n"
        "Selected cluster material:\n\n"
        + "\n\n".join(cluster_blocks)
    )


def prepare_related_work_material(
    project_id: str,
    problem: str,
    cluster_keys: list[str],
) -> dict[str, object]:
    from koi.review.artifacts import _paper_answer_artifact_from_dict

    normalized_problem = str(problem or "").strip()
    if not normalized_problem:
        raise ValueError("Problem statement must not be empty.")

    payload = load_latest_paper_answer_run(project_id)
    if payload is None:
        raise ValueError("No saved paper answer run was found for this project.")

    raw_papers = payload.get("papers")
    if not isinstance(raw_papers, list) or not raw_papers:
        raise ValueError("Latest paper answer run does not contain paper summaries.")

    artifacts: list[PaperAnswerArtifact] = []
    for item in raw_papers:
        if not isinstance(item, dict):
            continue
        artifact = _paper_answer_artifact_from_dict(item)
        if artifact is not None:
            artifacts.append(artifact)
    if not artifacts:
        raise ValueError("Latest paper answer run does not contain valid paper artifacts.")

    valid_titles = tuple(artifact.title for artifact in artifacts)
    clusters = _parse_paper_answer_clusters(
        {"clusters": payload.get("clusters")},
        valid_titles=valid_titles,
    )
    if not clusters:
        raise ValueError("Latest paper answer run does not contain valid answer clusters.")

    wanted = {str(key).strip() for key in cluster_keys if str(key).strip()}
    if not wanted:
        raise ValueError("Select at least one cluster before generating Related Works.")

    selected_clusters = [cluster for cluster in clusters if cluster.key in wanted]
    if not selected_clusters:
        raise ValueError("Selected clusters were not found in the latest paper answer run.")

    selected_titles = {title for cluster in selected_clusters for title in cluster.paper_titles}
    selected_artifacts = [artifact for artifact in artifacts if artifact.title in selected_titles]
    prompt = _build_related_works_prompt(
        project_id=project_id,
        question=str(payload.get("question") or ""),
        problem=normalized_problem,
        clusters=selected_clusters,
        artifacts=selected_artifacts,
    )
    return {
        "project_id": project_id,
        "question": str(payload.get("question") or ""),
        "problem": normalized_problem,
        "cluster_keys": [cluster.key for cluster in selected_clusters],
        "cluster_labels": [cluster.label for cluster in selected_clusters],
        "paper_count": len(selected_artifacts),
        "prompt": prompt,
    }

def generate_related_works_section(
    project_id: str,
    problem: str,
    cluster_keys: list[str],
) -> dict[str, object]:
    material = prepare_related_work_material(project_id, problem, cluster_keys)
    text, backend = run_agent(str(material["prompt"]), cwd=get_workspace().agent_cwd())
    markdown = _strip_code_fences(text or "").strip()
    if not markdown:
        raise RuntimeError("No agent backend is available for Related Works generation.")

    return {
        "project_id": project_id,
        "question": material["question"],
        "problem": material["problem"],
        "cluster_keys": material["cluster_keys"],
        "cluster_labels": material["cluster_labels"],
        "paper_count": material["paper_count"],
        "backend": backend,
        "markdown": markdown,
        "status": "answered",
    }


__all__ = ["generate_related_works_section", "prepare_related_work_material"]
