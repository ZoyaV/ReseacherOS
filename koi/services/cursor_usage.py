"""Compatibility facade for :mod:`koi.cursor.usage`."""
import sys

from koi.cursor import usage as _module

sys.modules[__name__] = _module
