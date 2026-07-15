"""Tests for kanban DAG layout sidecar JSON."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from koi.core.models import ExperimentCard, KanbanBoard, Project
from koi.services.dag_layout import (
    load_dag_layout,
    load_dag_layouts_from_root,
    normalize_cards,
    save_dag_layout,
)

try:
    from fastapi.testclient import TestClient

    from api.main import app

    HAS_FASTAPI = True
except ImportError:  # pragma: no cover - dev env without API deps
    HAS_FASTAPI = False


class DagLayoutServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.koi_root = Path(self.tmp.name) / "koi-structure"
        self.koi_root.mkdir(parents=True)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_save_load_and_filter_unknown_cards(self) -> None:
        with patch("koi.services.dag_layout.dag_layout_path") as path_mock, patch(
            "koi.services.dag_layout.dag_layouts_dir",
            return_value=self.koi_root / "dag-layouts",
        ):
            path_mock.side_effect = lambda _pid, board_id: self.koi_root / "dag-layouts" / f"{board_id}.json"
            saved = save_dag_layout(
                "demo",
                "board-m1",
                {
                    "c-a": {"x": 72, "y": 56},
                    "c-b": {"x": 400, "y": 120},
                    "bad": {"x": "nope", "y": 1},
                },
                valid_card_ids={"c-a", "c-b"},
            )
            self.assertEqual(saved["cards"]["c-a"], {"x": 72.0, "y": 56.0})
            self.assertNotIn("bad", saved["cards"])

            loaded = load_dag_layout("demo", "board-m1")
            self.assertEqual(loaded["cards"], saved["cards"])
            file_path = self.koi_root / "dag-layouts" / "board-m1.json"
            self.assertTrue(file_path.is_file())
            stored = json.loads(file_path.read_text(encoding="utf-8"))
            self.assertEqual(stored["version"], 1)
            self.assertEqual(stored["board_id"], "board-m1")

    def test_load_dag_layouts_from_root(self) -> None:
        layouts_dir = self.koi_root / "dag-layouts"
        layouts_dir.mkdir(parents=True)
        (layouts_dir / "board-m1.json").write_text(
            json.dumps(
                {
                    "version": 1,
                    "board_id": "board-m1",
                    "cards": {"c-a": {"x": 10, "y": 20}},
                }
            ),
            encoding="utf-8",
        )
        bundle = load_dag_layouts_from_root(self.koi_root)
        self.assertIn("board-m1", bundle)
        self.assertEqual(bundle["board-m1"]["cards"]["c-a"], {"x": 10.0, "y": 20.0})

    def test_normalize_cards_rejects_out_of_bounds(self) -> None:
        cleaned = normalize_cards({"c-a": {"x": 9000, "y": 10}})
        self.assertEqual(cleaned, {})


class DagLayoutApiTests(unittest.TestCase):
    @unittest.skipUnless(HAS_FASTAPI, "fastapi not installed")
    def test_get_and_put_board_layout(self) -> None:
        client = TestClient(app)
        board = KanbanBoard(
            id="board-m1",
            owner_node_id="m1",
            cards=[
                ExperimentCard(
                    id="c-a",
                    board_id="board-m1",
                    column_id="backlog",
                    title="A",
                )
            ],
        )
        project = Project(id="demo", title="Demo", boards=[board])

        with patch("api.routers.projects.parse_project", return_value=project), patch(
            "api.routers.projects.require_project", return_value=project
        ), patch("koi.services.dag_layout.save_dag_layout") as save_mock, patch(
            "koi.services.dag_layout.load_dag_layout",
            return_value={
                "version": 1,
                "board_id": "board-m1",
                "updated_at": None,
                "cards": {},
            },
        ) as load_mock:
            get_resp = client.get("/projects/demo/boards/board-m1/dag-layout")
            self.assertEqual(get_resp.status_code, 200)
            load_mock.assert_called_once_with("demo", "board-m1")

            put_resp = client.put(
                "/projects/demo/boards/board-m1/dag-layout",
                json={"cards": {"c-a": {"x": 12, "y": 34}}},
            )
            self.assertEqual(put_resp.status_code, 200)
            save_mock.assert_called_once_with(
                "demo",
                "board-m1",
                {"c-a": {"x": 12, "y": 34}},
                valid_card_ids={"c-a"},
            )
