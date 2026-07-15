from __future__ import annotations

import json
import re

from koi.review.models import ANSWER_STRATEGIES, ANSWER_STRATEGY_BY_KEY, PaperSummary, ReviewPaper
from koi.review.util import _normalize_text, _tokenize

def _unique_in_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


CLUSTER_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "been", "being", "by", "can", "could",
    "did", "do", "does", "for", "from", "had", "has", "have", "how", "however", "in",
    "into", "is", "it", "its", "just", "may", "might", "must", "new", "no", "not", "of",
    "on", "one", "or", "our", "paper", "present", "propose", "show", "shows", "such",
    "than", "that", "the", "their", "them", "then", "there", "these", "they", "this",
    "those", "through", "to", "two", "using", "was", "we", "well", "were", "which",
    "while", "will", "with", "would",
}


def _meaningful_tokens(text: str) -> set[str]:
    return {
        token
        for token in _tokenize(text)
        if token not in CLUSTER_STOPWORDS and len(token) > 2
    }


def _paper_summary_text(
    paper: ReviewPaper,
    summary: PaperSummary,
    *,
    include_title: bool = False,
) -> str:
    return " ".join(
        [part for part in [
            paper.title if include_title else "",
            paper.abstract,
            summary.core_idea,
            summary.representation_of_dynamics,
            summary.evidence,
            summary.usefulness,
        ] if part]
    )


def _distinct_sentences(sentences: list[str], limit: int = 3) -> tuple[str, ...]:
    seen: set[str] = set()
    picked: list[str] = []
    for sentence in sentences:
        normalized = _normalize_text(sentence)
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        picked.append(normalized)
        if len(picked) >= limit:
            break
    return tuple(picked)


def _quote_excerpt(text: str, *, limit: int = 180) -> str:
    compact = _normalize_text(text)
    if len(compact) <= limit:
        return compact
    clipped = compact[:limit].rsplit(" ", 1)[0].rstrip(" ,;:")
    return f"{clipped}..."


def _strip_code_fences(text: str) -> str:
    stripped = (text or "").strip()
    if not stripped.startswith("```"):
        return stripped
    stripped = re.sub(r"^```[a-zA-Z0-9_-]*\s*", "", stripped)
    stripped = re.sub(r"\s*```$", "", stripped)
    return stripped.strip()


def _extract_json_object(text: str) -> dict[str, object] | None:
    stripped = _strip_code_fences(text)
    candidates = [stripped]
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start != -1 and end != -1 and end > start:
        candidates.append(stripped[start : end + 1])
    for candidate in candidates:
        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            return parsed
    return None


def _normalize_llm_evidence(value: object, *, limit: int = 8) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ()
    snippets: list[str] = []
    for item in value:
        if not isinstance(item, str):
            continue
        compact = _normalize_text(item)
        if compact:
            snippets.append(compact)
    return _distinct_sentences(snippets, limit=limit)


def _normalize_llm_terms(value: object, *, limit: int = 8) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ()
    terms: list[str] = []
    for item in value:
        if not isinstance(item, str):
            continue
        compact = _normalize_text(item)
        if compact:
            terms.append(compact)
    return tuple(_unique_in_order(terms)[:limit])


def _strategy_catalog_text() -> str:
    lines = []
    for strategy in ANSWER_STRATEGIES:
        lines.append(f"- {strategy.key}: {strategy.label} — {strategy.answer_hint}")
    return "\n".join(lines)


def _normalize_strategy_key(value: object) -> str | None:
    key = _normalize_text(str(value or "")).lower().replace(" ", "_").replace("-", "_")
    return key if key in ANSWER_STRATEGY_BY_KEY else None
