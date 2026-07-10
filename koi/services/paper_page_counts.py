"""Estimate main / references / appendix page counts for a paper slot."""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

TEX_NAME = "main.tex"
PDF_NAME = "paper.pdf"


def _find_pdf(slot_dir: Path) -> Path | None:
    preferred = slot_dir / PDF_NAME
    if preferred.is_file():
        return preferred
    main_pdf = slot_dir / "main.pdf"
    if main_pdf.is_file():
        return main_pdf
    pdfs = sorted(
        p for p in slot_dir.glob("*.pdf") if p.is_file() and not p.name.startswith(".")
    )
    return pdfs[0] if len(pdfs) == 1 else None

BIB_RE = re.compile(
    r"\\(?:bibliography|printbibliography|begin\{thebibliography\})",
    re.IGNORECASE,
)
APPENDIX_RE = re.compile(r"\\(?:appendix|begin\{appendices\})", re.IGNORECASE)
REF_TITLE_RE = re.compile(r"\b(references|bibliography)\b", re.IGNORECASE)
APP_TITLE_RE = re.compile(r"\b(appendix|appendices)\b", re.IGNORECASE)


def _find_marker_line(tex: str, pattern: re.Pattern[str]) -> int | None:
    match = pattern.search(tex)
    if not match:
        return None
    return tex[: match.start()].count("\n") + 1


def _synctex_page(pdf: Path, tex_name: str, line: int) -> int | None:
    if line < 1 or not shutil.which("synctex"):
        return None
    proc = subprocess.run(
        [
            "synctex",
            "view",
            "-i",
            f"{line}:0:{tex_name}",
            "-o",
            pdf.name,
        ],
        cwd=pdf.parent,
        capture_output=True,
        text=True,
    )
    out = proc.stdout + proc.stderr
    match = re.search(r"Page:(\d+)", out)
    if not match:
        return None
    return int(match.group(1))


def count_pdf_pages(pdf_path: Path) -> int:
    from pypdf import PdfReader

    return len(PdfReader(str(pdf_path)).pages)


def _split_pages(
    total: int,
    *,
    bib_page: int | None,
    appendix_page: int | None,
) -> dict[str, int]:
    if total <= 0:
        return {"total": 0, "main": 0, "references": 0, "appendix": 0}

    if bib_page is None and appendix_page is None:
        return {"total": total, "main": total, "references": 0, "appendix": 0}

    if bib_page is not None and appendix_page is not None:
        main_end = max(0, min(bib_page - 1, total))
        if appendix_page <= bib_page:
            references = max(0, total - main_end)
            appendix = 0
        else:
            references = max(0, appendix_page - bib_page)
            appendix = max(0, total - appendix_page + 1)
        return {
            "total": total,
            "main": main_end,
            "references": references,
            "appendix": appendix,
        }

    if bib_page is not None:
        main_end = max(0, min(bib_page - 1, total))
        return {
            "total": total,
            "main": main_end,
            "references": max(0, total - main_end),
            "appendix": 0,
        }

    assert appendix_page is not None
    main_end = max(0, min(appendix_page - 1, total))
    return {
        "total": total,
        "main": main_end,
        "references": 0,
        "appendix": max(0, total - main_end),
    }


def _heuristic_marker_pages(pdf_path: Path, total: int) -> tuple[int | None, int | None]:
    from pypdf import PdfReader

    reader = PdfReader(str(pdf_path))
    ref_page: int | None = None
    app_page: int | None = None
    for index, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        page_no = index + 1
        if ref_page is None and REF_TITLE_RE.search(text):
            ref_page = page_no
        if app_page is None and APP_TITLE_RE.search(text):
            app_page = page_no
    if ref_page is not None and ref_page > total:
        ref_page = None
    if app_page is not None and app_page > total:
        app_page = None
    return ref_page, app_page


def analyze_paper_pages(slot_dir: Path) -> dict[str, int | str] | None:
    """Return page counts for main body, references, and appendix."""
    pdf = _find_pdf(slot_dir)
    if pdf is None or not pdf.is_file():
        return None

    total = count_pdf_pages(pdf)
    tex_path = slot_dir / TEX_NAME
    bib_page: int | None = None
    appendix_page: int | None = None
    method = "total_only"

    if tex_path.is_file():
        tex = tex_path.read_text(encoding="utf-8")
        bib_line = _find_marker_line(tex, BIB_RE)
        appendix_line = _find_marker_line(tex, APPENDIX_RE)
        if bib_line is not None:
            bib_page = _synctex_page(pdf, tex_path.name, bib_line)
        if appendix_line is not None:
            appendix_page = _synctex_page(pdf, tex_path.name, appendix_line)
        if bib_page is not None or appendix_page is not None:
            method = "synctex"

    if bib_page is None and appendix_page is None:
        bib_page, appendix_page = _heuristic_marker_pages(pdf, total)
        if bib_page is not None or appendix_page is not None:
            method = "heuristic"

    counts = _split_pages(total, bib_page=bib_page, appendix_page=appendix_page)
    counts["method"] = method
    return counts
