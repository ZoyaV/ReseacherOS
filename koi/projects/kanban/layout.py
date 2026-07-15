"""Persist kanban DAG card positions in ``koi-structure/dag-layouts/<board_id>.json``."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from koi.adapters.paths import dag_layout_path, dag_layouts_dir

SCHEMA_VERSION = 1
BOARD_ID_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._-]{0,127}$")


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _empty_layout(board_id: str) -> dict[str, Any]:
    return {
        "version": SCHEMA_VERSION,
        "board_id": board_id,
        "updated_at": None,
        "cards": {},
    }


def _sanitize_board_id(board_id: str) -> str:
    cleaned = board_id.strip()
    if not BOARD_ID_RE.fullmatch(cleaned):
        raise ValueError("Invalid board id")
    return cleaned


def _sanitize_position(raw: Any) -> dict[str, float] | None:
    if not isinstance(raw, dict):
        return None
    try:
        x = float(raw.get("x"))
        y = float(raw.get("y"))
    except (TypeError, ValueError):
        return None
    if not (abs(x) < 1e9 and abs(y) < 1e9):
        return None
    if x < -240 or y < -240 or x > 8000 or y > 8000:
        return None
    return {"x": x, "y": y}


def normalize_cards(
    cards: dict[str, Any] | None,
    *,
    valid_card_ids: set[str] | None = None,
) -> dict[str, dict[str, float]]:
    if not isinstance(cards, dict):
        return {}
    out: dict[str, dict[str, float]] = {}
    for card_id, pos in cards.items():
        if not isinstance(card_id, str) or not card_id.strip():
            continue
        if valid_card_ids is not None and card_id not in valid_card_ids:
            continue
        cleaned = _sanitize_position(pos)
        if cleaned is not None:
            out[card_id] = cleaned
    return out


def load_dag_layout(project_id: str, board_id: str) -> dict[str, Any]:
    board_id = _sanitize_board_id(board_id)
    path = dag_layout_path(project_id, board_id)
    if not path.is_file():
        return _empty_layout(board_id)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return _empty_layout(board_id)
    if not isinstance(data, dict):
        return _empty_layout(board_id)
    cards = normalize_cards(data.get("cards"))
    return {
        "version": SCHEMA_VERSION,
        "board_id": board_id,
        "updated_at": data.get("updated_at"),
        "cards": cards,
    }


def save_dag_layout(
    project_id: str,
    board_id: str,
    cards: dict[str, Any],
    *,
    valid_card_ids: set[str] | None = None,
) -> dict[str, Any]:
    board_id = _sanitize_board_id(board_id)
    cleaned = normalize_cards(cards, valid_card_ids=valid_card_ids)
    payload = {
        "version": SCHEMA_VERSION,
        "board_id": board_id,
        "updated_at": _now_iso(),
        "cards": cleaned,
    }
    layouts_dir = dag_layouts_dir(project_id)
    layouts_dir.mkdir(parents=True, exist_ok=True)
    path = dag_layout_path(project_id, board_id)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


def load_dag_layouts_from_root(koi_root: Path) -> dict[str, dict[str, Any]]:
    """Read all board layouts from a koi-structure directory (Hub sync)."""
    root = koi_root / "dag-layouts"
    if not root.is_dir():
        return {}
    layouts: dict[str, dict[str, Any]] = {}
    for path in sorted(root.glob("*.json")):
        board_id = path.stem
        if not BOARD_ID_RE.fullmatch(board_id):
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(data, dict):
            continue
        layouts[board_id] = {
            "version": SCHEMA_VERSION,
            "board_id": board_id,
            "updated_at": data.get("updated_at"),
            "cards": normalize_cards(data.get("cards")),
        }
    return layouts
