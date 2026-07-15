"""Compatibility facade — use :mod:`koi.agent_chat.inbox`."""
import sys

from koi.agent_chat import inbox as _module

sys.modules[__name__] = _module
