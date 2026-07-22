"""arXiv search, query translation, and API bootstrap."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

from koi.adapters.agent_backends import run_agent
from koi.adapters.workspace import get_workspace
from koi.literature.library import (
    ARXIV_API_URL,
    ARXIV_ATOM_NS,
    ARXIV_MAX_QUERY_TERMS,
    ARXIV_QUERY_STOPWORDS,
    ARXIV_QUERY_WEAK_TERMS,
    ARXIV_TOKEN_RE,
    CYRILLIC_RE,
    LIBRARY_FIELDNAMES,
    LIBRARY_REQUIRED_FIELDS,
    LIBRARY_UPLOAD_PATH,
    AgentDiscoveredPaper,
    _display_path,
    _normalize_arxiv_url,
    _normalize_spaces,
    _snippet,
    _tokenize,
    _write_library_csv,
    infer_year_from_arxiv_url,
    reset_library_cache,
)

def _needs_translation(text: str) -> bool:
    return bool(CYRILLIC_RE.search(text))


def _arxiv_query_tokens(text: str, *, max_terms: int = ARXIV_MAX_QUERY_TERMS) -> list[str]:
    raw = [m.group(0) for m in ARXIV_TOKEN_RE.finditer((text or "").lower())]
    seen: set[str] = set()
    candidates: list[str] = []
    for token in raw:
        if token in ARXIV_QUERY_STOPWORDS or len(token) < 2:
            continue
        if token in seen:
            continue
        seen.add(token)
        candidates.append(token)

    if not candidates:
        candidates = [token for token in raw if len(token) >= 2]
        if not candidates:
            return []

    def rank(token: str) -> tuple[int, int, int, int]:
        is_weak = token in ARXIV_QUERY_WEAK_TERMS
        is_acronym = len(token) <= 5 and (token.isupper() or token in {"ctr", "llm", "ppo", "nlp", "rl"})
        has_hyphen = "-" in token
        is_specific = len(token) >= 6 or token in {"ctr", "ads", "ad"}
        return (0 if is_weak else 1, is_acronym or has_hyphen, is_specific, len(token))

    candidates.sort(key=rank, reverse=True)
    strong = [token for token in candidates if token not in ARXIV_QUERY_WEAK_TERMS]
    weak = [token for token in candidates if token in ARXIV_QUERY_WEAK_TERMS]
    ordered = strong + weak
    return ordered[: max(1, max_terms)]


def _build_arxiv_search_query(text: str, *, max_terms: int = ARXIV_MAX_QUERY_TERMS) -> str:
    tokens = _arxiv_query_tokens(text, max_terms=max_terms)
    if not tokens:
        return ""
    if len(tokens) == 1:
        return f"all:{tokens[0]}"
    return "+AND+".join(f"all:{token}" for token in tokens)


def _fetch_arxiv_atom(search_q: str, limit: int) -> bytes | None:
    from urllib.parse import quote

    if not search_q:
        return None
    max_results = max(1, min(limit, 50))
    url = (
        f"{ARXIV_API_URL}?search_query={quote(search_q, safe='+:')}"
        f"&start=0&max_results={max_results}&sortBy=relevance&sortOrder=descending"
    )
    request = urllib.request.Request(url, headers={"User-Agent": "ResearchOS/1.0 (arxiv-api)"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.read()
    except (OSError, TimeoutError, urllib.error.URLError, urllib.error.HTTPError):
        return None


def _parse_arxiv_atom_feed(xml_bytes: bytes, query: str, limit: int) -> list[dict[str, object]]:
    root = ET.fromstring(xml_bytes)
    query_token_set = set(_arxiv_query_tokens(query, max_terms=12))
    if not query_token_set:
        query_token_set = set(_tokenize(query))
    results: list[tuple[float, dict[str, object]]] = []
    max_results = max(1, min(limit, 50))

    for idx, entry in enumerate(root.findall("atom:entry", ARXIV_ATOM_NS)):
        title = _normalize_spaces(entry.findtext("atom:title", default="", namespaces=ARXIV_ATOM_NS))
        summary = _normalize_spaces(entry.findtext("atom:summary", default="", namespaces=ARXIV_ATOM_NS))
        entry_id = entry.findtext("atom:id", default="", namespaces=ARXIV_ATOM_NS).strip()
        arxiv_url = _normalize_arxiv_url(entry_id) or entry_id

        authors: list[str] = []
        for author in entry.findall("atom:author", ARXIV_ATOM_NS):
            name = _normalize_spaces(author.findtext("atom:name", default="", namespaces=ARXIV_ATOM_NS))
            if name:
                authors.append(name)

        if not title or not arxiv_url:
            continue

        title_tokens = set(_tokenize(title))
        abstract_tokens = set(_tokenize(summary))
        overlap = sorted(query_token_set & (title_tokens | abstract_tokens))
        title_overlap = len(query_token_set & title_tokens)
        relevance = title_overlap * 2.0 + len(overlap) - idx * 0.05
        results.append(
            (
                relevance,
                {
                    "title": title,
                    "arxiv_url": arxiv_url,
                    "authors": ", ".join(authors),
                    "year": infer_year_from_arxiv_url(arxiv_url),
                    "abstract": summary,
                    "abstract_preview": _snippet(summary, query_token_set)
                    if query_token_set
                    else short_preview(summary),
                    "score": round(max(0.65, 1.0 - idx * 0.03), 3),
                    "matched_terms": overlap,
                },
            )
        )

    results.sort(key=lambda item: item[0], reverse=True)
    return [item[1] for item in results[:max_results]]


def short_preview(text: str, max_chars: int = 280) -> str:
    normalized = _normalize_spaces(text)
    if len(normalized) <= max_chars:
        return normalized
    return normalized[: max_chars - 1].rstrip() + "…"


def search_arxiv_internet(query: str, limit: int = 10) -> list[dict[str, object]]:
    text = _normalize_spaces(query)
    if not text:
        return []

    all_tokens = _arxiv_query_tokens(text, max_terms=12)
    if not all_tokens:
        return []

    term_budgets = []
    for count in (ARXIV_MAX_QUERY_TERMS, 2, 1):
        if count not in term_budgets:
            term_budgets.append(count)

    for count in term_budgets:
        if len(all_tokens) < count:
            continue
        tokens = all_tokens[:count]
        if len(tokens) == 1:
            search_q = f"all:{tokens[0]}"
        else:
            search_q = "+AND+".join(f"all:{token}" for token in tokens)
        xml_bytes = _fetch_arxiv_atom(search_q, limit)
        if not xml_bytes:
            continue
        results = _parse_arxiv_atom_feed(xml_bytes, text, limit)
        if results:
            return results

    return []


def _translate_via_openrouter(text: str) -> tuple[str | None, str | None]:
    from koi.adapters.agent_backends import run_openrouter

    prompt = (
        "Translate the following literature-search question into natural, concise academic English.\n"
        "Preserve technical meaning and line breaks.\n"
        "Return only the translated English text.\n\n"
        f"{text}"
    )
    translated = run_openrouter(prompt, timeout=90)
    if translated:
        return translated.strip().strip('"'), "openrouter"
    return None, None


def _translate_via_mymemory(text: str) -> tuple[str | None, str | None]:
    from urllib.parse import quote

    chunk = text[:480]
    url = f"https://api.mymemory.translated.net/get?q={quote(chunk)}&langpair=ru|en"
    request = urllib.request.Request(url, headers={"User-Agent": "ResearchOS/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            payload = json.loads(response.read().decode("utf-8", errors="replace"))
    except (OSError, TimeoutError, urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError):
        return None, None

    translated = _normalize_spaces(
        str(((payload.get("responseData") or {}).get("translatedText")) or "")
    )
    if not translated or translated.upper() == chunk.upper():
        return None, None
    return translated, "mymemory"


def translate_to_english(text: str) -> tuple[str, str]:
    normalized = _normalize_spaces(text)
    if not normalized:
        return "", "none"
    if not _needs_translation(normalized):
        return normalized, "passthrough"

    prompt = (
        "Translate the following literature-search question into natural, concise academic English.\n"
        "Preserve technical meaning, paper titles, identifiers, bullet structure, and line breaks.\n"
        "Do not add explanations, notes, quotes, markdown fences, or any extra commentary.\n"
        "Return only the translated English text.\n\n"
        f"{normalized}"
    )
    translated, backend = run_agent(prompt, cwd=get_workspace().agent_cwd(), timeout=120)
    if translated:
        return translated.strip().strip('"'), backend or "agent"

    translated, backend = _translate_via_openrouter(normalized)
    if translated:
        return translated, backend

    translated, backend = _translate_via_mymemory(normalized)
    if translated:
        return translated, backend

    return normalized, "original"


def bootstrap_library_from_arxiv(
    query: str,
    limit: int = 10,
    *,
    destination: Path = LIBRARY_UPLOAD_PATH,
) -> dict[str, object]:
    text = _normalize_spaces(query)
    if not text:
        raise ValueError("Query must not be empty")
    if limit < 1:
        raise ValueError("Limit must be positive")

    results = search_arxiv_internet(text, min(limit, 50))
    if not results:
        raise RuntimeError("No papers found on arXiv for this query.")

    papers = [
        AgentDiscoveredPaper(
            title=str(result["title"]),
            arxiv_url=str(result["arxiv_url"]),
            authors=str(result.get("authors") or ""),
            abstract=str(result.get("abstract") or ""),
        )
        for result in results
    ]
    _write_library_csv(papers, destination)
    reset_library_cache()

    return {
        "ok": True,
        "query": text,
        "count": len(papers),
        "csv_path": _display_path(destination),
        "fields": list(LIBRARY_FIELDNAMES),
        "required_fields": list(LIBRARY_REQUIRED_FIELDS),
        "backend": "arxiv_api",
        "notes": "Imported from arXiv API search.",
        "papers": [
            {
                "title": paper.title,
                "arxiv_url": paper.arxiv_url,
                "authors": paper.authors,
                "abstract": paper.abstract,
            }
            for paper in papers
        ],
    }
