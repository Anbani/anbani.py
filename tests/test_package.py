import subprocess
import sys


def test_public_api_is_exposed():
    import anbani

    assert callable(anbani.convert)
    assert callable(anbani.interpret)
    assert callable(anbani.classify_text)


def test_import_is_lightweight():
    # `import anbani` must not pull in heavy / optional dependencies, nor the
    # nlp subpackage. Run in a fresh interpreter so test-ordering can't pollute
    # sys.modules.
    code = (
        "import anbani, sys; "
        "assert 'pandas' not in sys.modules, 'pandas leaked'; "
        "assert 'numpy' not in sys.modules, 'numpy leaked'; "
        "assert 'pymupdf' not in sys.modules and 'fitz' not in sys.modules, 'pymupdf leaked'; "
        "assert 'anbani.nlp' not in sys.modules, 'nlp leaked'; "
        "assert 'anbani.tui' not in sys.modules, 'tui leaked'; "
        "assert 'anbani.toolkit' not in sys.modules, 'toolkit eagerly loaded'; "
        "assert 'anbani.lorem' not in sys.modules, 'lorem eagerly loaded'"
    )
    subprocess.run([sys.executable, "-c", code], check=True)


def test_lazy_submodules_resolve():
    import anbani

    assert callable(anbani.toolkit.friedman)
    assert callable(anbani.lorem.sentences)
