# Lightweight public API. The `nlp` subpackage is intentionally NOT imported
# here so that `import anbani` stays cheap and free of heavy optional
# dependencies (PyMuPDF, ambigram/contraction tables). Import it explicitly:
#     from anbani.nlp.georgianisation import georgianise
#
# `toolkit` and `lorem` are stdlib-only and cheap, but exposed lazily via
# PEP 562 so `import anbani` still pulls in nothing but the core converter.
from .core.converter import classify_text, convert, interpret

__all__ = ["convert", "interpret", "classify_text", "toolkit", "lorem"]


def __getattr__(name):
    if name in ("toolkit", "lorem"):
        import importlib

        module = importlib.import_module(f".{name}", __name__)
        globals()[name] = module
        return module
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
