"""Compatibility facade — use :mod:`koi.paper.inbox`."""
import sys
from koi.paper import inbox as _module
sys.modules[__name__] = _module
