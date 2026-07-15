"""Compatibility facade — use :mod:`koi.agent_chat.formatting`."""
import sys

from koi.agent_chat import formatting as _module

sys.modules[__name__] = _module
