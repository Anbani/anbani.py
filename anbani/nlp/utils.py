"""PDF / e-book text extraction.

PyMuPDF is imported lazily inside :func:`ebook2text` so that importing this
module (and the rest of ``anbani.nlp``) does not require the optional
``pymupdf`` dependency.
"""

# Hyphen-like code points that, when followed by a newline, indicate a word
# split across lines and should be stitched back together.
_HYPHENS = (
    "-",   # 002D
    "‐",   # 2010
    "‑",   # 2011
    "‒",   # 2012
    "–",   # 2013
    "—",   # 2014
    "―",   # 2015
    "−",   # 2212
    "֊",   # 058A
    "⁻",   # 207B
    "₋",   # 208B
    "⸺",  # 2E3A
    "⸻",  # 2E3B
    "﹘",  # FE58
    "－",  # FF0D
    "﹣",  # FE63
)


def _import_pymupdf():
    try:
        import pymupdf  # PyMuPDF >= 1.24
        return pymupdf
    except ImportError:
        try:
            import fitz  # older PyMuPDF exposes the module as `fitz`
            return fitz
        except ImportError as e:
            raise ImportError(
                "ebook2text requires the optional 'pymupdf' dependency. "
                "Install it with: pip install pymupdf"
            ) from e


def ebook2text(path):
    """Extract and lightly clean text from the PDF / e-book at ``path``.

    Returns the extracted text, or a ``"Error: ..."`` string if extraction
    fails. Raises :class:`ImportError` if PyMuPDF is not installed.
    """
    pymupdf = _import_pymupdf()

    try:
        doc = pymupdf.open(path)
        text = "".join(
            doc.load_page(p).get_text() for p in range(doc.page_count)
        )

        # Reconnect words split by a hyphen at a line break
        for hyphen in _HYPHENS:
            text = text.replace(hyphen + "\n", "")

        # Flatten the remaining (paragraph / random) newlines
        text = text.replace("\n", " ")
    except Exception as e:
        return "Error: " + str(e)

    return text
