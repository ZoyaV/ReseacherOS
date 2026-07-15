"""Compatibility facade for the canonical :mod:`koi.review` package."""
import sys
from importlib import import_module

import koi.review as _module

sys.modules[f"{__name__}.analysis"] = import_module("koi.review.analysis")

for _name in (
    "arxiv",
    "artifacts",
    "clustering",
    "models",
    "parsing",
    "papers",
    "pipeline",
    "related_work",
    "rendering",
    "storage",
    "summaries",
    "util",
):
    sys.modules[f"{__name__}.{_name}"] = getattr(_module, _name)

sys.modules[__name__] = _module
