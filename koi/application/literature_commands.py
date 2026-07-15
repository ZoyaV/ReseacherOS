"""Compatibility facade — use :mod:`koi.literature.review_sets`."""
import sys

from koi.literature import review_sets as _module

sys.modules[__name__] = _module
