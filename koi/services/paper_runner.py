"""Compatibility facade — use :mod:`koi.paper.runner`."""
import sys
from koi.paper import runner as _module
sys.modules[__name__] = _module
