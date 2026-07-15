from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from koi.review.arxiv import extract_arxiv_id
from koi.review.models import (
    PaperAnswerArtifact, PaperAnswerCluster, PaperArtifact, PaperSummary,
    ProposedCluster, ReviewPaper,
)
from koi.review.parsing import _quote_excerpt

def build_paper_summary_markdown(
    paper: ReviewPaper,
    summary: PaperSummary,
    *,
    rank: int,
    html_path: Path | None,
    pdf_path: Path | None,
    text_path: Path | None,
    extracted_text_chars: int,
    summary_backend: str | None,
    cluster: ProposedCluster,
    cluster_assignment_rationale: str,
) -> str:
    score_text = f"{paper.score:.3f}" if paper.score is not None else "n/a"
    matched_terms = ", ".join(paper.matched_terms) if paper.matched_terms else "n/a"
    full_text_status = "yes" if extracted_text_chars > 0 else "no"
    evidence_snippets = (
        " ".join(f'"{_quote_excerpt(snippet)}"' for snippet in summary.answer_evidence)
        if summary.answer_evidence
        else "No direct evidence snippet extracted."
    )
    return (
        f"# {paper.title}\n\n"
        f"- Rank: {rank}\n"
        f"- Query: {paper.query or 'n/a'}\n"
        f"- Score: {score_text}\n"
        f"- ArXiv: {paper.arxiv_url}\n"
        f"- ArXiv ID: {extract_arxiv_id(paper.arxiv_url)}\n"
        f"- Source report: {paper.source_report}\n"
        f"- Matched terms: {matched_terms}\n"
        f"- Full text extracted: {full_text_status}\n"
        f"- Extracted text chars: {extracted_text_chars}\n"
        f"- HTML cache: {html_path.name if html_path else 'not available'}\n"
        f"- PDF cache: {pdf_path.name if pdf_path else 'not available'}\n"
        f"- Text cache: {text_path.name if text_path else 'not available'}\n"
        f"- Summary backend: {summary_backend or 'n/a'}\n\n"
        "## Abstract\n\n"
        f"{paper.abstract or 'No abstract available.'}\n\n"
        "## Auto Summary\n\n"
        f"**Core idea.** {summary.core_idea}\n\n"
        f"**How dynamics are represented.** {summary.representation_of_dynamics}\n\n"
        f"**Direct answer to the query.** {summary.query_answer}\n\n"
        f"**Answer strategy.** {summary.answer_strategy_label}\n\n"
        f"**Evidence snippets.** {evidence_snippets}\n\n"
        f"**Evidence / setup.** {summary.evidence}\n\n"
        f"**Why it matters for the question.** {summary.usefulness}\n\n"
        f"**Limitations / caution.** {summary.limitations}\n\n"
        "## Cluster Assignment\n\n"
        f"- Proposed answer family: {cluster.answer_hint}\n"
        f"- Assigned cluster: {cluster.label}\n"
        f"- Cluster key: {cluster.key}\n"
        f"- Assignment rationale: {cluster_assignment_rationale}\n"
    )


def build_paper_question_markdown(
    paper: ReviewPaper,
    *,
    question: str,
    rank: int,
    html_path: Path | None,
    pdf_path: Path | None,
    text_path: Path | None,
    extracted_text_chars: int,
    answer_backend: str | None,
    answer_source: str,
    short_answer: str,
    comprehensive_answer: str,
    evidence: tuple[str, ...],
    limitations: str,
) -> str:
    score_text = f"{paper.score:.3f}" if paper.score is not None else "n/a"
    matched_terms = ", ".join(paper.matched_terms) if paper.matched_terms else "n/a"
    full_text_status = "yes" if extracted_text_chars > 0 else "no"
    evidence_block = (
        "\n".join(f"- \"{_quote_excerpt(snippet, limit=320)}\"" for snippet in evidence)
        if evidence
        else "- No direct evidence snippet extracted."
    )
    return (
        f"# {paper.title}\n\n"
        f"- Rank: {rank}\n"
        f"- Question: {question or 'n/a'}\n"
        f"- Score: {score_text}\n"
        f"- ArXiv: {paper.arxiv_url}\n"
        f"- ArXiv ID: {extract_arxiv_id(paper.arxiv_url)}\n"
        f"- Source report: {paper.source_report}\n"
        f"- Matched terms: {matched_terms}\n"
        f"- Full text extracted: {full_text_status}\n"
        f"- Extracted text chars: {extracted_text_chars}\n"
        f"- HTML cache: {html_path.name if html_path else 'not available'}\n"
        f"- PDF cache: {pdf_path.name if pdf_path else 'not available'}\n"
        f"- Text cache: {text_path.name if text_path else 'not available'}\n\n"
        "## Answer Generation\n\n"
        f"- Source: {answer_source}\n"
        f"- Backend: {answer_backend or 'n/a'}\n\n"
        "## Abstract\n\n"
        f"{paper.abstract or 'No abstract available.'}\n\n"
        "## Direct Answer\n\n"
        f"{short_answer}\n\n"
        "## Detailed Answer\n\n"
        f"{comprehensive_answer}\n\n"
        "## Evidence From The Paper\n\n"
        f"{evidence_block}\n\n"
        "## Limitations / Caution\n\n"
        f"{limitations}\n"
    )


def build_question_answer_index_markdown(
    question: str,
    artifacts: list[PaperAnswerArtifact],
    *,
    clusters: list[PaperAnswerCluster] | None = None,
    cluster_report_path: str | None = None,
) -> str:
    lines = [
        "# Paper Answers",
        "",
        f"- Question: {question or 'n/a'}",
        f"- Generated at: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}",
        f"- Papers analyzed: {len(artifacts)}",
        f"- Cluster report: {cluster_report_path or 'n/a'}",
        "",
    ]
    if clusters:
        lines.extend(
            [
                "## Proposed Clusters",
                "",
            ]
        )
        for cluster in clusters:
            lines.extend(
                [
                    f"### {cluster.label}",
                    "",
                    f"**Cluster answer.** {cluster.answer}",
                    "",
                    f"**Why this cluster should exist.** {cluster.rationale}",
                    "",
                    f"**How it differs.** {cluster.distinguishing_features}",
                    "",
                    f"**Papers.** {', '.join(cluster.paper_titles)}",
                    "",
                ]
            )

    lines.extend(
        [
        "## Answers",
        "",
        ]
    )
    for artifact in artifacts:
        lines.extend(
            [
                f"### {artifact.title}",
                "",
                f"**Direct answer.** {artifact.short_answer}",
                "",
                f"**Backend.** {artifact.answer_backend or 'n/a'}",
                "",
                f"**Cluster.** {artifact.cluster_label or 'n/a'}",
                "",
            ]
        )
        if artifact.evidence:
            lines.append(f"**Top evidence.** \"{_quote_excerpt(artifact.evidence[0], limit=260)}\"")
            lines.append("")
    return "\n".join(lines).strip() + "\n"


def build_paper_answer_cluster_report(
    question: str,
    artifacts: list[PaperAnswerArtifact],
    clusters: list[PaperAnswerCluster],
    *,
    cluster_backend: str | None,
) -> str:
    artifact_by_title = {artifact.title: artifact for artifact in artifacts}
    lines = [
        "# Answer Clusters",
        "",
        f"- Question: {question or 'n/a'}",
        f"- Generated at: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}",
        f"- Cluster backend: {cluster_backend or 'n/a'}",
        f"- Papers analyzed: {len(artifacts)}",
        "",
        "## Reading Of The Answer Files",
        "",
        "These clusters were proposed from the per-paper answer markdown files, not from title-level heuristics or keyword grouping.",
        "",
    ]
    for cluster in clusters:
        lines.extend(
            [
                f"## {cluster.label}",
                "",
                f"**Shared answer.** {cluster.answer}",
                "",
                f"**Why this cluster should exist.** {cluster.rationale}",
                "",
                f"**How it differs from nearby clusters.** {cluster.distinguishing_features}",
                "",
                f"**Signature terms.** {', '.join(cluster.signature_terms) if cluster.signature_terms else 'n/a'}",
                "",
                "**Papers in this cluster.**",
            ]
        )
        for title in cluster.paper_titles:
            artifact = artifact_by_title.get(title)
            if artifact is None:
                continue
            lines.append(f"- {artifact.title}: {artifact.short_answer}")
            lines.append(f"  - Why assigned here: {artifact.cluster_rationale or cluster.rationale}")
            for snippet in artifact.evidence[:2]:
                lines.append(f"  - Evidence: \"{_quote_excerpt(snippet)}\"")
        lines.append("")
    return "\n".join(lines).strip() + "\n"



def build_cluster_report(
    query: str,
    clusters: list[ProposedCluster],
    artifacts: list[PaperArtifact],
    summaries: dict[str, PaperSummary],
) -> str:
    grouped: dict[str, list[PaperArtifact]] = {cluster.key: [] for cluster in clusters}
    for artifact in artifacts:
        grouped.setdefault(artifact.cluster_key, []).append(artifact)

    lines = [
        "# Cluster Directions",
        "",
        f"- Query: {query or 'n/a'}",
        f"- Generated at: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}",
        f"- Papers analyzed: {len(artifacts)}",
        "",
        "## Reading Of The Literature",
        "",
        "These clusters describe different ways the literature answers the question, not just different application areas.",
        "",
    ]

    lines.extend(
        [
            "## Proposed Clusters",
            "",
            "The agent proposed these clusters after reading the paper summaries and looking for repeated answer patterns.",
            "",
        ]
    )

    for cluster in clusters:
        lines.append(f"- {cluster.label}: {cluster.rationale}")
    lines.append("")

    for cluster in clusters:
        members = grouped.get(cluster.key, [])
        if not members:
            continue
        lines.extend(
            [
                f"## {cluster.label}",
                "",
                f"**Answer to the question.** {cluster.answer}",
                "",
                f"**Cluster answer hint.** {cluster.answer_hint}",
                "",
                f"**Suggested research direction.** {cluster.direction}",
                "",
                f"**Signature terms.** {', '.join(cluster.signature_terms) if cluster.signature_terms else 'n/a'}",
                "",
                "**Papers in this answer family.**",
            ]
        )
        for artifact in members:
            summary = summaries[artifact.title]
            lines.append(
                f"- {artifact.title}: {summary.query_answer}"
            )
            for snippet in summary.answer_evidence[:2]:
                lines.append(f"  - Evidence: \"{_quote_excerpt(snippet)}\"")
        lines.append("")

    return "\n".join(lines).strip() + "\n"
