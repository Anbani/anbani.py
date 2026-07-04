import importlib.util

import pytest

from anbani.nlp.utils import ebook2text

_HAS_PYMUPDF = (
    importlib.util.find_spec("pymupdf") is not None
    or importlib.util.find_spec("fitz") is not None
)


@pytest.mark.skipif(not _HAS_PYMUPDF, reason="pymupdf not installed")
def test_ebook2text_bad_path_returns_error_string():
    assert ebook2text("definitely_does_not_exist.pdf").startswith("Error:")


@pytest.mark.skipif(_HAS_PYMUPDF, reason="pymupdf is installed")
def test_ebook2text_without_pymupdf_raises_importerror():
    with pytest.raises(ImportError):
        ebook2text("anything.pdf")
