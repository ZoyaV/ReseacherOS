"""Compatibility facade for :mod:`koi.cursor.app`."""
import sys

from koi.cursor import app as _module

sys.modules[__name__] = _module
