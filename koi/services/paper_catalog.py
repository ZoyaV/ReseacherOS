"""Compatibility facade — use :mod:`koi.paper.catalog`."""
import sys
from koi.paper import catalog as _module
sys.modules[__name__] = _module
