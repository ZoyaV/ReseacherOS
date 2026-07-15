"""Compatibility facade for the canonical :mod:`koi.review` package."""
import sys

import koi.review as _module

for _name in (
    "analysis",
    "arxiv",
    "artifacts",
    "models",
    "papers",
    "pipeline",
    "storage",
    "util",
):
    sys.modules[f"{__name__}.{_name}"] = getattr(_module, _name)

sys.modules[__name__] = _module
