"""Compatibility facade for the decomposed review analysis modules."""

from koi.review import clustering, parsing, related_work, rendering, summaries

_MODULES = (parsing, summaries, clustering, rendering, related_work)

for _module in _MODULES:
    for _name in dir(_module):
        if _name.startswith("__"):
            continue
        globals()[_name] = getattr(_module, _name)

del _module, _name, _MODULES
