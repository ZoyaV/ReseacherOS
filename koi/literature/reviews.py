"""Paper-review artifact creation for the literature capability."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from koi.adapters.paths import paper_reviews_dir
from koi.literature.naming import safe_filename as _safe_filename
from koi.literature.naming import slugify as _slugify

PAPER_REVIEWS_DIRNAME = "paper_reviews"

def review_project_title(query: str, max_len: int = 72) -> str:
    title = f"Review Set: {query.strip()}"
    return title if len(title) <= max_len else title[: max_len - 1].rstrip() + "…"


def review_project_description(query: str, result_count: int) -> str:
    return (
        f"Research question: {query.strip()}\n\n"
        f"This project was generated automatically from the local literature library. "
        f"It contains {result_count} ranked paper candidates for screening and annotation."
    )


def build_review_report(result: dict[str, object], query: str) -> str:
    matched = result.get("matched_terms") or []
    matched_text = ", ".join(str(x) for x in matched) if matched else "n/a"
    abstract = str(result.get("abstract") or "").strip()
    return (
        f"# {result['title']}\n\n"
        f"- Query: {query.strip()}\n"
        f"- Score: {result['score']}\n"
        f"- ArXiv: {result['arxiv_url']}\n"
        f"- Matched terms: {matched_text}\n\n"
        "## Abstract\n\n"
        f"{abstract or 'No abstract available.'}\n\n"
        "## Screening Notes\n\n"
        "- Relevance:\n"
        "- Key contribution:\n"
        "- Useful methods / datasets:\n"
        "- Decision:\n"
    )


def review_card_id() -> str:
    return f"c-{uuid4().hex[:8]}"


def _paper_reviews_root(project_id: str) -> Path:
    return paper_reviews_dir(project_id)


def _paper_reviews_index_path(project_id: str) -> Path:
    return _paper_reviews_root(project_id) / "index.json"


def _load_paper_reviews_index(project_id: str) -> list[dict[str, object]]:
    path = _paper_reviews_index_path(project_id)
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def _save_paper_reviews_index(project_id: str, entries: list[dict[str, object]]) -> None:
    path = _paper_reviews_index_path(project_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(entries, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _unique_review_dir(project_id: str, query: str) -> Path:
    root = _paper_reviews_root(project_id)
    root.mkdir(parents=True, exist_ok=True)
    base = _slugify(query, fallback="paper-review")
    candidate = root / base
    n = 1
    while candidate.exists():
        n += 1
        candidate = root / f"{base}-{n}"
    return candidate


def create_project_paper_review(
    project_id: str, query: str, results: list[dict[str, object]]
) -> dict[str, object]:
    review_dir = _unique_review_dir(project_id, query)
    review_dir.mkdir(parents=True, exist_ok=True)
    created_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    papers_meta: list[dict[str, object]] = []
    for idx, result in enumerate(results, start=1):
        filename = f"{idx:02d}_{_safe_filename(str(result['title']), fallback=f'paper_{idx:02d}')}"
        content = build_review_report(result, query)
        (review_dir / filename).write_text(content, encoding="utf-8")
        papers_meta.append(
            {
                "rank": idx,
                "title": result["title"],
                "arxiv_url": result["arxiv_url"],
                "score": result.get("score"),
                "filename": filename,
            }
        )

    manifest = {
        "query": query.strip(),
        "created_at": created_at,
        "count": len(results),
        "papers": papers_meta,
    }
    (review_dir / "index.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    top_index = _load_paper_reviews_index(project_id)
    top_index.append(
        {
            "folder": review_dir.name,
            "query": query.strip(),
            "created_at": created_at,
            "count": len(results),
            "path": f"{PAPER_REVIEWS_DIRNAME}/{review_dir.name}",
        }
    )
    _save_paper_reviews_index(project_id, top_index)

    return {
        "project_id": project_id,
        "query": query.strip(),
        "count": len(results),
        "folder": review_dir.name,
        "path": f"{PAPER_REVIEWS_DIRNAME}/{review_dir.name}",
        "papers": papers_meta,
    }
