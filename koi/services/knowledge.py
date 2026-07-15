"""Compatibility facade — use :mod:`koi.knowledge`."""
import sys

from koi import knowledge as _module

sys.modules[__name__] = _module
