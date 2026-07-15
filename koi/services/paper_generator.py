"""Compatibility facade — use :mod:`koi.paper.generator`."""
import sys
from koi.paper import generator as _module
sys.modules[__name__] = _module
