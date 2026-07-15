"""Compatibility facade for :mod:`koi.related_work.service`."""
import sys

from koi.related_work import service as _module

sys.modules[__name__] = _module
