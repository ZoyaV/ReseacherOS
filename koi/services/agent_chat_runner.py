"""Compatibility facade — use :mod:`koi.agent_chat.runner`."""
import sys

from koi.agent_chat import runner as _module

sys.modules[__name__] = _module
