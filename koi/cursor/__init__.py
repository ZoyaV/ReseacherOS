"""Cursor IDE integration capability."""

from koi.cursor.app import (
    cursor_frontmost_app_name,
    cursor_is_active,
    cursor_is_frontmost,
    cursor_is_running,
)
from koi.cursor.usage import CursorUsageSnapshot, fetch_cursor_usage

__all__ = [
    "CursorUsageSnapshot",
    "cursor_frontmost_app_name",
    "cursor_is_active",
    "cursor_is_frontmost",
    "cursor_is_running",
    "fetch_cursor_usage",
]
