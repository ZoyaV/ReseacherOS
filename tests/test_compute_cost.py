from __future__ import annotations

from koi.projects.compute_cost import (
    format_compute_cost_line,
    format_hours_short,
    merge_compute_cost,
    parse_compute_cost,
    parse_hours_value,
)


def test_parse_hours_value_units() -> None:
    assert parse_hours_value("0.13") == 0.13
    assert parse_hours_value("0,13h") == 0.13
    assert abs(parse_hours_value("7.6m") - 7.6 / 60) < 1e-9
    assert abs(parse_hours_value("90s") - 90 / 3600) < 1e-9
    assert parse_hours_value("") is None
    assert parse_hours_value("nope") is None


def test_parse_compute_cost_semicolon() -> None:
    text = """# Card

compute_cost: wall_h=0.13; gpu_h=0.13; n_gpus=1; until=SMA SR≥0.8; source=recovered

## 1. Body
"""
    cost = parse_compute_cost(text)
    assert cost is not None
    assert cost["wall_h"] == 0.13
    assert cost["gpu_h"] == 0.13
    assert cost["n_gpus"] == 1
    assert cost["until"] == "SMA SR≥0.8"
    assert cost["source"] == "recovered"


def test_parse_compute_cost_space_separated() -> None:
    text = "live_note: x\ncompute_cost: wall_h=2.4 gpu_h=4.8 n_gpus=2\n"
    cost = parse_compute_cost(text)
    assert cost is not None
    assert cost["wall_h"] == 2.4
    assert cost["gpu_h"] == 4.8
    assert cost["n_gpus"] == 2
    assert cost["source"] == "measured"


def test_parse_compute_cost_optional_absent() -> None:
    assert parse_compute_cost("# no cost\n") is None
    assert parse_compute_cost("compute_cost: until=only") is None
    assert parse_compute_cost("compute_cost:   ") is None


def test_format_hours_short() -> None:
    assert format_hours_short(0.13) == "7.8m"
    assert format_hours_short(2.4) == "2.4h"
    assert format_hours_short(12) == "12h"


def test_format_and_merge() -> None:
    line = format_compute_cost_line(
        {"wall_h": 0.13, "gpu_h": 0.13, "n_gpus": 1, "until": "SR≥0.8", "source": "recovered"}
    )
    assert line.startswith("compute_cost:")
    assert "source=recovered" in line
    assert merge_compute_cost("desc", line)["wall_h"] == 0.13
    assert merge_compute_cost("compute_cost: wall_h=1", "compute_cost: wall_h=9")["wall_h"] == 1
