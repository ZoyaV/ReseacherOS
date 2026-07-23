"""Optional compute-cost line in card reports / descriptions.

Agents may add a single optional header line (same style as ``live_log:``):

    compute_cost: wall_h=0.13; gpu_h=0.13; n_gpus=1; until=SMA SR≥0.8; source=measured

All keys are optional. Omit the line entirely when cost is unknown or irrelevant
(literature cards, analysis-only work).

Keys
----
wall_h
    Wall-clock hours for the measured span (job, or until a metric threshold).
gpu_h
    GPU-hours ≈ wall_h × n_gpus when GPUs are held exclusively; otherwise measured.
n_gpus
    Number of GPUs held for that span.
until
    Free-text milestone (prefer with ``;`` separators so spaces are allowed).
source
    ``measured`` (default) | ``estimated`` | ``recovered`` (backfilled from old logs).
"""

from __future__ import annotations

import re
from typing import Any

COMPUTE_COST_RE = re.compile(r"^compute_cost:\s*(.+)$", re.MULTILINE | re.IGNORECASE)
_PAIR_RE = re.compile(r"([a-z_]+)\s*=\s*(.+)", re.IGNORECASE)
_HOURS_RE = re.compile(
    r"^([+-]?\d+(?:[.,]\d+)?)\s*(h|hr|hrs|hours|m|min|mins|minutes|s|sec|secs)?$",
    re.IGNORECASE,
)
_INT_RE = re.compile(r"^(\d+)\s*$")

VALID_SOURCES = frozenset({"measured", "estimated", "recovered"})


def parse_hours_value(raw: str | None) -> float | None:
    """Parse ``0.13``, ``0,13h``, ``7.6m``, ``90s`` into hours."""
    if raw is None:
        return None
    s = str(raw).strip()
    if not s:
        return None
    m = _HOURS_RE.match(s)
    if not m:
        return None
    n = float(m.group(1).replace(",", "."))
    unit = (m.group(2) or "h").lower()
    if unit.startswith("m"):
        return n / 60.0
    if unit.startswith("s"):
        return n / 3600.0
    return n


def _split_pairs(raw: str) -> list[str]:
    text = str(raw or "").strip()
    if not text:
        return []
    if ";" in text:
        return [chunk.strip() for chunk in text.split(";") if chunk.strip()]
    return [m.group(0) for m in re.finditer(r"[a-z_]+\s*=\s*\S+", text, flags=re.I)]


def parse_compute_cost(text: str | None) -> dict[str, Any] | None:
    """Extract structured compute cost from report/description text, or None."""
    body = str(text or "").replace("\\n", "\n")
    m = COMPUTE_COST_RE.search(body)
    if not m:
        return None
    raw = m.group(1).strip()
    if not raw:
        return None

    fields: dict[str, str] = {}
    for chunk in _split_pairs(raw):
        pm = _PAIR_RE.match(chunk.strip())
        if not pm:
            continue
        key = pm.group(1).strip().lower()
        fields[key] = pm.group(2).strip()

    if not fields:
        return None

    out: dict[str, Any] = {"raw": raw}
    wall = parse_hours_value(fields.get("wall_h") or fields.get("wall"))
    gpu = parse_hours_value(fields.get("gpu_h") or fields.get("gpu") or fields.get("gpu_hours"))
    if wall is not None:
        out["wall_h"] = wall
    if gpu is not None:
        out["gpu_h"] = gpu

    n_raw = fields.get("n_gpus") or fields.get("gpus") or fields.get("n_gpu")
    if n_raw is not None:
        im = _INT_RE.match(str(n_raw).strip())
        if im:
            out["n_gpus"] = int(im.group(1))

    until = fields.get("until") or fields.get("to")
    if until:
        out["until"] = until

    source = (fields.get("source") or "measured").strip().lower()
    out["source"] = source if source in VALID_SOURCES else "measured"

    if "wall_h" not in out and "gpu_h" not in out:
        return None
    return out


def format_hours_short(hours: float | None) -> str | None:
    """Compact human label for UI chips."""
    if hours is None:
        return None
    try:
        h = float(hours)
    except (TypeError, ValueError):
        return None
    if h < 0:
        return None
    if h < 1 / 60:
        sec = max(1, round(h * 3600))
        return f"{sec}s"
    if h < 1:
        mins = h * 60
        if mins < 10:
            label = f"{mins:.1f}".rstrip("0").rstrip(".")
        else:
            label = str(round(mins))
        return f"{label}m"
    if h < 10:
        label = f"{h:.2f}".rstrip("0").rstrip(".")
    else:
        label = f"{h:.1f}".rstrip("0").rstrip(".")
    return f"{label}h"


def format_compute_cost_line(cost: dict[str, Any]) -> str:
    """Serialize a cost dict back to a ``compute_cost:`` header line."""
    parts: list[str] = []
    if cost.get("wall_h") is not None:
        parts.append(f"wall_h={cost['wall_h']}")
    if cost.get("gpu_h") is not None:
        parts.append(f"gpu_h={cost['gpu_h']}")
    if cost.get("n_gpus") is not None:
        parts.append(f"n_gpus={cost['n_gpus']}")
    if cost.get("until"):
        parts.append(f"until={cost['until']}")
    source = cost.get("source") or "measured"
    if source != "measured":
        parts.append(f"source={source}")
    return "compute_cost: " + "; ".join(parts)


def merge_compute_cost(*sources: str | None) -> dict[str, Any] | None:
    """First non-empty parse wins (description before report is typical)."""
    for src in sources:
        parsed = parse_compute_cost(src)
        if parsed:
            return parsed
    return None
