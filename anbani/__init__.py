# Lightweight public API. The `nlp` subpackage is intentionally NOT imported
# here so that `import anbani` stays cheap and free of heavy optional
# dependencies (PyMuPDF, pandas, numpy). Import it explicitly when needed:
#     from anbani.nlp.georgianisation import georgianise
from .core.converter import classify_text, convert, interpret

__all__ = ["convert", "interpret", "classify_text"]
