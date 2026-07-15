"""Tests for kanban DAG suggestion helpers."""

from __future__ import annotations

from koi.core.models import ExperimentCard, KanbanBoard, Node, NodeType, Project
from koi.projects.kanban.dependencies import (
    _normalize_dep_ids,
    _would_create_cycle,
    apply_dag_suggestions,
    normalize_dependency_ids,
    suggest_board_dag,
)


def _sample_board() -> tuple[Project, KanbanBoard]:
    project = Project(id="p1", title="P")
    method = Node(
        id="m1",
        project_id="p1",
        parent_id="root",
        node_type=NodeType.METHOD,
        title="Method",
        research_questions=[],
    )
    board = KanbanBoard(
        id="board-m1",
        owner_node_id="m1",
        cards=[
            ExperimentCard(
                id="c-done",
                board_id="board-m1",
                column_id="done",
                title="Segment audit",
                description="budget and CTR by groups",
            ),
            ExperimentCard(
                id="c-open",
                board_id="board-m1",
                column_id="backlog",
                title="Cross tab groups and targeting",
                description="continue segment audit with cross table",
            ),
        ],
    )
    project.nodes = [method]
    project.boards = [board]
    return project, board


def test_suggest_links_done_to_backlog_by_overlap() -> None:
    project, board = _sample_board()
    suggestions = suggest_board_dag(project, board, include_reports=False)
    assert any(
        s["from_card_id"] == "c-done" and s["to_card_id"] == "c-open"
        for s in suggestions
    )


def test_normalize_rejects_cycles() -> None:
    _, board = _sample_board()
    card = board.cards[0]
    card.depends_on = []
    board.cards[1].depends_on = ["c-done"]
    from koi.projects.kanban.dependencies import _normalize_dep_ids, _would_create_cycle

    candidate = _normalize_dep_ids(["c-open"], {c.id for c in board.cards}, "c-done")
    assert _would_create_cycle(board.cards, "c-done", candidate)


def test_normalize_allows_clearing_deps() -> None:
    _, board = _sample_board()
    board.cards[1].depends_on = ["c-done"]
    cleared = _normalize_dep_ids([], {c.id for c in board.cards}, "c-open")
    assert cleared == []
    assert not _would_create_cycle(board.cards, "c-open", cleared)


def test_normalize_dependencies_preserves_order_and_removes_invalid_ids() -> None:
    normalized = normalize_dependency_ids(
        ["c-open", "missing", "c-open", "c-done"],
        {"c-done", "c-open"},
        "c-done",
    )

    assert normalized == ["c-open"]


def test_apply_dag_suggestions_updates_each_card_once() -> None:
    _, board = _sample_board()
    suggestions = [
        {
            "from_card_id": "c-done",
            "to_card_id": "c-open",
            "confidence": 0.9,
        },
        {
            "from_card_id": "c-done",
            "to_card_id": "c-open",
            "confidence": 0.8,
        },
    ]

    assert apply_dag_suggestions(board, suggestions) == 1
    assert board.cards[1].depends_on == ["c-done"]
