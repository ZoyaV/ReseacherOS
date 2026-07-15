"""Paper review agent — layered implementation."""

from koi.review import (
    arxiv,
    artifacts,
    clustering,
    models,
    parsing,
    papers,
    pipeline,
    related_work,
    rendering,
    storage,
    summaries,
    util,
)

_SUBMODULES = (
    arxiv,
    artifacts,
    clustering,
    models,
    parsing,
    papers,
    pipeline,
    related_work,
    rendering,
    storage,
    summaries,
    util,
)

for _mod in _SUBMODULES:
    for _name in dir(_mod):
        if _name.startswith("__"):
            continue
        globals()[_name] = getattr(_mod, _name)

del _mod, _name, _SUBMODULES
