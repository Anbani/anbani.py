import subprocess
import sys


def test_public_api_is_exposed():
    import anbani

    assert callable(anbani.convert)
    assert callable(anbani.interpret)
    assert callable(anbani.classify_text)


def test_import_is_lightweight():
    # `import anbani` must not pull in heavy / optional dependencies. Run in a
    # fresh interpreter so test-ordering can't pollute sys.modules.
    code = (
        "import anbani, sys; "
        "assert 'pandas' not in sys.modules, 'pandas leaked'; "
        "assert 'numpy' not in sys.modules, 'numpy leaked'; "
        "assert 'pymupdf' not in sys.modules and 'fitz' not in sys.modules, 'pymupdf leaked'"
    )
    subprocess.run([sys.executable, "-c", code], check=True)
