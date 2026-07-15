"""Compatibility facade — use :mod:`koi.paper.page_counts`."""
import sys
from koi.paper import page_counts as _module
sys.modules[__name__] = _module
