"""Compatibility facade — use :mod:`koi.literature`."""
import sys

from koi import literature as _module

sys.modules[__name__] = _module
