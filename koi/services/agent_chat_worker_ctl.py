"""Compatibility facade — use :mod:`koi.agent_chat.worker`."""
import sys

from koi.agent_chat import worker as _module

sys.modules[__name__] = _module
