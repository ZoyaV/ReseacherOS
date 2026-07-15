"""Compatibility facade for :mod:`koi.related_work.inbox`."""
import sys

from koi.related_work import inbox as _module

sys.modules[__name__] = _module
