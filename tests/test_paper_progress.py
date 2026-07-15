"""Tests for paper page counting and progress metadata."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from koi.paper.catalog import (
    deadline_hours_left,
    list_project_papers,
    read_paper_progress,
    update_paper_progress,
)
from koi.paper.page_counts import _split_pages, analyze_paper_pages


class PaperPageCountTests(unittest.TestCase):
    def test_split_pages_with_bibliography_and_appendix(self) -> None:
        counts = _split_pages(10, bib_page=8, appendix_page=10)
        self.assertEqual(counts["main"], 7)
        self.assertEqual(counts["references"], 2)
        self.assertEqual(counts["appendix"], 1)

    def test_split_pages_without_markers(self) -> None:
        counts = _split_pages(6, bib_page=None, appendix_page=None)
        self.assertEqual(counts["main"], 6)
        self.assertEqual(counts["references"], 0)
        self.assertEqual(counts["appendix"], 0)

    def test_analyze_paper_pages_from_tex_markers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            slot = Path(tmp)
            tex = slot / "main.tex"
            tex.write_text(
                "\n".join(
                    [
                        "\\documentclass{article}",
                        "\\begin{document}",
                        "Main body",
                        "\\bibliography{refs}",
                        "\\appendix",
                        "Appendix text",
                        "\\end{document}",
                    ]
                ),
                encoding="utf-8",
            )
            pdf = slot / "main.pdf"
            pdf.write_bytes(b"%PDF-1.4\n")

            with patch(
                "koi.paper.page_counts.count_pdf_pages",
                return_value=10,
            ), patch(
                "koi.paper.page_counts._synctex_page",
                side_effect=[8, 10],
            ):
                counts = analyze_paper_pages(slot)

            self.assertIsNotNone(counts)
            assert counts is not None
            self.assertEqual(counts["total"], 10)
            self.assertEqual(counts["main"], 7)
            self.assertEqual(counts["references"], 2)
            self.assertEqual(counts["appendix"], 1)
            self.assertEqual(counts["method"], "synctex")


class PaperProgressMetaTests(unittest.TestCase):
    def test_read_and_update_progress(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            slot = Path(tmp)
            (slot / "main.tex").write_text("% paper", encoding="utf-8")
            (slot / "paper.json").write_text(
                json.dumps({"title": "Demo", "progress": {"main_pages": 5}}),
                encoding="utf-8",
            )

            progress = read_paper_progress(json.loads((slot / "paper.json").read_text()))
            self.assertEqual(progress["main_pages"], 5)
            self.assertIsNone(progress["references_pages"])

            updated = update_paper_progress(
                slot,
                {
                    "references_pages": 2,
                    "deadline": "2030-01-01T12:00:00+00:00",
                },
            )
            self.assertEqual(updated["references_pages"], 2)
            self.assertEqual(updated["deadline"], "2030-01-01T12:00:00+00:00")

    def test_list_project_papers_includes_progress(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paper_root = Path(tmp) / "paper"
            slot = paper_root / "demo-paper"
            slot.mkdir(parents=True)
            (slot / "main.tex").write_text("% demo", encoding="utf-8")
            (slot / "paper.json").write_text(
                json.dumps(
                    {
                        "title": "Demo",
                        "progress": {
                            "main_pages": 8,
                            "deadline": "2030-06-01",
                        },
                    }
                ),
                encoding="utf-8",
            )

            with patch("koi.paper.catalog.paper_dir", return_value=paper_root):
                papers = list_project_papers("demo")

            self.assertEqual(len(papers), 1)
            self.assertEqual(papers[0]["progress"]["main_pages"], 8)
            self.assertIsNotNone(papers[0]["deadline_hours_left"])
            self.assertIsNone(papers[0]["page_counts"])

    def test_deadline_hours_left_for_date_only(self) -> None:
        hours = deadline_hours_left("2099-12-31")
        self.assertIsNotNone(hours)
        assert hours is not None
        self.assertGreater(hours, 24)


if __name__ == "__main__":
    unittest.main()
