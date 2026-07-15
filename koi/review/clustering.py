from __future__ import annotations

from collections import Counter

from koi.adapters.agent_backends import run_agent
from koi.adapters.settings_store import load_env_file
from koi.adapters.workspace import get_workspace
from koi.literature.naming import slugify as _slugify
from koi.review.models import (
    ANSWER_STRATEGIES, ANSWER_STRATEGY_BY_KEY, PaperAnswerArtifact,
    PaperAnswerCluster, PaperSummary, ProposedCluster, ReviewPaper,
)
from koi.review.parsing import (
    _distinct_sentences, _extract_json_object, _meaningful_tokens,
    _normalize_llm_terms, _paper_summary_text,
    _quote_excerpt, _unique_in_order,
)
from koi.review.util import _normalize_text

def _paper_answer_token_set(artifact: PaperAnswerArtifact) -> set[str]:
    title_tokens = _meaningful_tokens(artifact.title)
    if len(title_tokens) >= 2:
        return title_tokens
    return _meaningful_tokens(
        " ".join([artifact.title, artifact.short_answer[:400], artifact.comprehensive_answer[:400]])
    )


def _token_jaccard(left: set[str], right: set[str]) -> float:
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


def _build_cluster_from_members(
    question: str,
    members: list[PaperAnswerArtifact],
    *,
    index: int,
) -> PaperAnswerCluster:
    term_counts: Counter[str] = Counter()
    for member in members:
        term_counts.update(_paper_answer_token_set(member))
    signature_terms = tuple(term for term, _count in term_counts.most_common(6) if term)
    label_terms = signature_terms[:3] or ("papers",)
    label = " · ".join(term.replace("-", " ") for term in label_terms).title()
    shared_answer = (
        f"Papers in this group share themes around {', '.join(signature_terms[:4]) or 'related topics'} "
        f"for: {question}"
    )
    key = _slugify(label, fallback=f"answer-cluster-{index:02d}")
    return PaperAnswerCluster(
        key=key,
        label=label,
        answer=shared_answer,
        rationale=f"Grouped {len(members)} paper(s) by title and topic token overlap.",
        distinguishing_features="Heuristic cluster from abstract/title overlap without LLM.",
        signature_terms=signature_terms,
        paper_titles=tuple(member.title for member in members),
    )


def _split_cluster_if_diverse(members: list[PaperAnswerArtifact]) -> list[list[PaperAnswerArtifact]]:
    if len(members) < 4:
        return [members]

    token_sets = {member.title: _paper_answer_token_set(member) for member in members}
    avg_similarity: dict[str, float] = {}
    for member in members:
        others = [other for other in members if other.title != member.title]
        if not others:
            avg_similarity[member.title] = 1.0
            continue
        avg_similarity[member.title] = sum(
            _token_jaccard(token_sets[member.title], token_sets[other.title]) for other in others
        ) / len(others)

    outlier = min(members, key=lambda member: avg_similarity[member.title])
    if avg_similarity[outlier.title] >= 0.18:
        return [members]

    group_a = [outlier]
    group_b = [member for member in members if member.title != outlier.title]
    if len(group_b) < 1:
        return [members]
    return [group_a, group_b]


def _cluster_paper_answers_heuristic(
    question: str,
    artifacts: list[PaperAnswerArtifact],
) -> list[PaperAnswerCluster]:
    if not artifacts:
        return []

    remaining = list(artifacts)
    grouped: list[list[PaperAnswerArtifact]] = []
    token_sets = {artifact.title: _paper_answer_token_set(artifact) for artifact in artifacts}

    while remaining:
        seed = remaining.pop(0)
        seed_tokens = token_sets[seed.title]
        members = [seed]
        next_remaining: list[PaperAnswerArtifact] = []
        for artifact in remaining:
            other_tokens = token_sets[artifact.title]
            overlap = _token_jaccard(seed_tokens, other_tokens)
            if overlap >= 0.22:
                members.append(artifact)
            else:
                next_remaining.append(artifact)
        remaining = next_remaining
        grouped.extend(_split_cluster_if_diverse(members))

    clusters: list[PaperAnswerCluster] = []
    for index, members in enumerate(grouped, start=1):
        clusters.append(_build_cluster_from_members(question, members, index=index))
    return clusters


def _normalize_cluster_titles(
    value: object,
    *,
    valid_titles: tuple[str, ...],
) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ()
    title_map = {_normalize_text(title).casefold(): title for title in valid_titles}
    matched: list[str] = []
    for item in value:
        if not isinstance(item, str):
            continue
        resolved = title_map.get(_normalize_text(item).casefold())
        if resolved:
            matched.append(resolved)
    return tuple(_unique_in_order(matched))


def _parse_paper_answer_clusters(
    payload: dict[str, object],
    *,
    valid_titles: tuple[str, ...],
) -> list[PaperAnswerCluster] | None:
    raw_clusters = payload.get("clusters")
    if not isinstance(raw_clusters, list) or not raw_clusters:
        return None

    clusters: list[PaperAnswerCluster] = []
    seen_keys: set[str] = set()
    assigned_titles: list[str] = []
    valid_title_set = set(valid_titles)

    for index, item in enumerate(raw_clusters, start=1):
        if not isinstance(item, dict):
            return None
        label = _normalize_text(str(item.get("label") or ""))
        answer = str(item.get("answer") or "").strip()
        rationale = str(item.get("rationale") or "").strip()
        distinguishing_features = str(item.get("distinguishing_features") or "").strip()
        paper_titles = _normalize_cluster_titles(
            item.get("paper_titles"),
            valid_titles=valid_titles,
        )
        signature_terms = _normalize_llm_terms(item.get("signature_terms"), limit=8)
        if not all([label, answer, rationale, distinguishing_features]) or not paper_titles:
            return None
        if not set(paper_titles).issubset(valid_title_set):
            return None
        key = _slugify(label, fallback=f"answer-cluster-{index}")
        if key in seen_keys:
            key = f"{key}-{index:02d}"
        seen_keys.add(key)
        assigned_titles.extend(paper_titles)
        clusters.append(
            PaperAnswerCluster(
                key=key,
                label=label,
                answer=answer,
                rationale=rationale,
                distinguishing_features=distinguishing_features,
                signature_terms=signature_terms,
                paper_titles=paper_titles,
            )
        )

    if set(assigned_titles) != valid_title_set:
        return None
    if len(assigned_titles) != len(valid_titles):
        return None
    return clusters


def _build_paper_answer_cluster_prompt(
    question: str,
    answer_documents: list[tuple[str, str]],
) -> str:
    docs_text = "\n\n".join(
        f"## Paper Answer File: {title}\n\n{content}" for title, content in answer_documents
    )
    return (
        "You are synthesizing a literature review from per-paper answer files.\n"
        "Your job is to propose clusters of papers based ONLY on the provided answer markdown files.\n"
        "Do not use background knowledge. Do not invent papers or merge papers by application area alone.\n"
        "Cluster papers by substantively different answers to the research question.\n"
        "Every paper must belong to exactly one cluster.\n"
        "The rationale for each cluster must explain why this cluster should exist as a distinct answer family.\n\n"
        "Return valid JSON only with this exact schema:\n"
        "{\n"
        '  "clusters": [\n'
        "    {\n"
        '      "label": string,\n'
        '      "answer": string,\n'
        '      "rationale": string,\n'
        '      "distinguishing_features": string,\n'
        '      "signature_terms": [string],\n'
        '      "paper_titles": [string]\n'
        "    }\n"
        "  ]\n"
        "}\n\n"
        "Field rules:\n"
        "- label: short cluster name.\n"
        "- answer: 1-3 sentences stating the common answer this cluster gives to the question.\n"
        "- rationale: 2-4 sentences arguing why these papers should be grouped together and why this cluster is distinct from the others.\n"
        "- distinguishing_features: 1-3 sentences naming the boundary of the cluster and how it differs from nearby clusters.\n"
        "- signature_terms: 3-8 short phrases that capture the cluster's answer.\n"
        "- paper_titles: exact paper titles from the provided files; every paper must appear exactly once across all clusters.\n\n"
        f"Research question: {question}\n\n"
        "Per-paper answer files:\n"
        f"{docs_text}\n"
    )


def _generate_paper_answer_clusters_with_llm(
    question: str,
    answer_documents: list[tuple[str, str]],
) -> tuple[list[PaperAnswerCluster] | None, str | None]:
    load_env_file()
    prompt = _build_paper_answer_cluster_prompt(question, answer_documents)
    text, backend = run_agent(prompt, cwd=get_workspace().agent_cwd())
    if not text:
        return None, backend
    payload = _extract_json_object(text)
    if not payload:
        return None, backend
    clusters = _parse_paper_answer_clusters(
        payload,
        valid_titles=tuple(title for title, _content in answer_documents),
    )
    return clusters, backend


def _assignment_rationale(
    paper: ReviewPaper,
    summary: PaperSummary,
    cluster: ProposedCluster,
) -> str:
    citations = list(summary.answer_evidence[:2]) or list(summary.citation_sentences[:2])
    lines = [
        f"This paper belongs in the cluster '{cluster.label}' because its answer strategy is '{summary.answer_strategy_label.lower()}'.",
        f"Its direct answer to the query is: {summary.query_answer}",
    ]
    if citations:
        lines.append(
            f"Key evidence: \"{_quote_excerpt(citations[0])}\"."
        )
    if len(citations) > 1:
        lines.append(
            f"Additional evidence: \"{_quote_excerpt(citations[1])}\"."
        )
    return " ".join(lines)


def propose_clusters(
    query: str,
    papers: list[ReviewPaper],
    summaries: dict[str, PaperSummary],
) -> list[ProposedCluster]:
    grouped: dict[str, list[tuple[ReviewPaper, PaperSummary]]] = {}
    for paper in papers:
        summary = summaries[paper.title]
        grouped.setdefault(summary.answer_strategy_key, []).append((paper, summary))

    clusters: list[ProposedCluster] = []
    grouped_sorted = sorted(
        grouped.items(),
        key=lambda item: (-len(item[1]), ANSWER_STRATEGY_BY_KEY[item[0]].label),
    )
    for index, (strategy_key, members) in enumerate(grouped_sorted, start=1):
        strategy = ANSWER_STRATEGY_BY_KEY.get(strategy_key, ANSWER_STRATEGY_BY_KEY["static_relational"])
        signature_terms = tuple(
            _unique_in_order(
                [term for _paper, summary in members for term in summary.signature_terms]
                + list(strategy.keywords[:3])
            )[:6]
        )
        rationale = (
            f"Grouped from {len(members)} paper(s) because the LLM assigned the same representation strategy: {strategy.answer_hint.lower()}"
        )
        clusters.append(
            ProposedCluster(
                key=f"cluster_{index:02d}_{_slugify(strategy.label, fallback='cluster')}",
                strategy_key=strategy.key,
                label=strategy.label,
                answer_hint=strategy.answer_hint,
                answer=strategy.answer if query else strategy.answer_hint,
                direction=strategy.direction,
                signature_terms=signature_terms,
                rationale=rationale,
            )
        )

    return clusters


def classify_papers_to_clusters(
    papers: list[ReviewPaper],
    summaries: dict[str, PaperSummary],
    clusters: list[ProposedCluster],
) -> dict[str, ProposedCluster]:
    cluster_by_strategy = {cluster.strategy_key: cluster for cluster in clusters}
    assignments: dict[str, ProposedCluster] = {}
    for paper in papers:
        summary = summaries[paper.title]
        cluster = cluster_by_strategy.get(summary.answer_strategy_key, clusters[0])
        assignments[paper.title] = cluster
    return assignments
