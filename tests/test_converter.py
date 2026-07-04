"""Tests for anbani.core.converter.

The "golden" cases below are ported verbatim from the anbani.js test suite
(test/index.test.mjs); both libraries share the same letters table, so the
expected outputs must match exactly.
"""

import pytest

import anbani
from anbani.core.converter import classify_text


# --- Golden cases shared with anbani.js -------------------------------------

def test_unicameral_mkhedruli_to_asomtavruli():
    assert anbani.convert("იყო არაბეთს როსტევან", "mkhedruli", "asomtavruli") == \
        "ႨႷႭ ႠႰႠႡႤႧႱ ႰႭႱႲႤႥႠႬ"


def test_unicameral_mkhedruli_to_mtavruli():
    assert anbani.convert("ანბანი", "mkhedruli", "mtavruli") == "ᲐᲜᲑᲐᲜᲘ"


def test_interpret_qwerty_to_mkhedruli():
    # Regression: classify_text() reports 'latin', which must resolve to 'qwerty'
    # instead of raising (previously an AssertionError).
    assert anbani.interpret("iyo arabeTs rostevan", "mkhedruli") == \
        "იყო არაბეთს როსტევან"


def test_bicameral_shanidziseuli():
    assert anbani.convert("ქართული ა'ნბანი", "mkhedruli", "shanidziseuli") == \
        "Ⴕართული Ⴀნბანი"


def test_bicameral_sasataure():
    assert anbani.convert("ქართული ა'ნბანი", "mkhedruli", "sasataure") == \
        "ႵᲐᲠᲗᲣᲚᲘ ႠᲜᲑᲐᲜᲘ"


# --- Bug-fix regressions ----------------------------------------------------

def test_empty_string_does_not_crash():
    # Previously raised IndexError on text[0] in the bicameral path.
    assert anbani.convert("", "mkhedruli", "sasataure") == ""
    assert anbani.convert("", "mkhedruli", "mtavruli") == ""


def test_unknown_source_raises_valueerror():
    # Previously an AssertionError (and silently disabled under `python -O`).
    with pytest.raises(ValueError):
        anbani.convert("ანბანი", "klingon", "mtavruli")


def test_unknown_target_raises_valueerror():
    # Previously returned the input unchanged with no error.
    with pytest.raises(ValueError):
        anbani.convert("ანბანი", "mkhedruli", "klingon")


def test_interpret_undetectable_raises_valueerror():
    with pytest.raises(ValueError):
        anbani.interpret("12345", "mtavruli")


def test_classify_text_is_not_anchored():
    # Regression for re.match -> re.search: leading non-letters must not hide
    # the script.
    assert classify_text("   რა ხდება") == "mkhedruli"
    assert classify_text("'rostevan'") == "latin"


def test_anbanismtavruli_back_compat_alias():
    assert anbani.convert("ანბანი", "mkhedruli", "anbanismtavruli") == \
        anbani.convert("ანბანი", "mkhedruli", "sasataure")


def test_punctuation_maps_after_data_sync():
    # The Python data table used to omit the punctuation rows, so '.' fell
    # through unconverted. After syncing with data.mjs it maps to braille.
    assert anbani.convert(".", "mkhedruli", "braille") == "⠲"


# --- 3.0: classify vector upgrade, braille source, bicameral interpret ------

def test_classify_detects_bicameral():
    assert classify_text("Ⴀანბანი") == "shanidziseuli"   # asomtavruli + mkhedruli
    assert classify_text("Ⴀⴀ") == "khutsuri"              # asomtavruli + nuskhuri


def test_classify_mixed_scripts_is_unknown():
    # Mixed Georgian + Latin no longer resolves to a single script.
    assert classify_text("ანბანabc") == "unknown"
    assert classify_text("") == "unknown"


def test_braille_as_source():
    assert anbani.convert("⠁⠃", "braille", "mkhedruli") == "აბ"


def test_interpret_bicameral_source():
    # Mixed-case Georgian is folded to its lower script, then converted.
    assert anbani.interpret("Ⴀა", "asomtavruli") == "ႠႠ"
