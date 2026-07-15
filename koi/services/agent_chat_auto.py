"""Compatibility facade — use :mod:`koi.agent_chat.auto`."""
import sys

from koi.agent_chat import auto as _module

sys.modules[__name__] = _module
