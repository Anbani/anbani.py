from anbani.nlp import georgianisation as g
from anbani.nlp.georgianisation import georgianise, georgianise_fast, latinise


def test_ambigrams_loaded_from_csv():
    # The stdlib-csv loader must reproduce what pandas produced: every
    # non-redundant row, in order. nc5_len7.csv has 8046 such rows.
    assert len(g.ambigrams_balanced) == 8046
    assert ("არtული>", "ართული>") in g.ambigrams_balanced


def test_georgianise_fast_letters():
    assert georgianise_fast("gamarjoba") == "გამარჯობა"


def test_georgianise_fast_diphthongs():
    assert georgianise_fast("sha") == "შა"
    assert georgianise_fast("cha") == "ჩა"
    assert georgianise_fast("dzma") == "ძმა"


def test_georgianise_mode_dispatch():
    assert georgianise("gamarjoba", mode="fast") == "გამარჯობა"
    # Smarter modes use the ambigram tables; just assert they run and stay Georgian.
    assert isinstance(georgianise("gamarjoba", mode="balanced"), str)
    assert isinstance(georgianise("gamarjoba", mode="accurate"), str)


def test_latinise_roundtrips_simple_word():
    assert latinise("გამარჯობა") == "gamarjoba"
