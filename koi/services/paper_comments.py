"""Compatibility facade — use :mod:`koi.paper.comments`."""
import sys
from koi.paper import comments as _module
sys.modules[__name__] = _module
