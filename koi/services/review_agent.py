"""Compatibility facade for the canonical :mod:`koi.review` package."""
import sys

import koi.review as _module

sys.modules[__name__] = _module
