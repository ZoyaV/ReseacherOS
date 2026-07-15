"""Stable naming helpers shared by literature and paper-review workflows."""

from __future__ import annotations

import re


def normalize_spaces(text: str) -> str:
    return " ".join((text or "").strip().split())


def slugify(text: str, fallback: str = "review") -> str:
    value = normalize_spaces(text).lower()
    value = re.sub(r"[^\w\s-]", "", value, flags=re.UNICODE)
    value = re.sub(r"[\s_]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value[:64] or fallback


def safe_filename(text: str, fallback: str = "paper") -> str:
    value = normalize_spaces(text)
    value = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "", value)
    value = re.sub(r"\s+", "_", value).strip(" ._")
    return (value[:120] or fallback) + ".md"
