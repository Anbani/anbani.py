"""Character statistics for cryptanalysis, ported from anbani.js `toolkit`.

`frequency`/`count` tally letters (case-folded to upper); `friedman` is the
index of coincidence. The default `miss` filter keeps Georgian (all four
scripts), Latin and Cyrillic letters and drops everything else.

Note on parity: JS iterates UTF-16 code units, Python iterates code points, so
results are identical for BMP text (Georgian/Latin/Cyrillic) but may differ for
astral characters. `frequency`'s denominator is the full string length,
including filtered-out characters — this is intentional and matches anbani.js.
"""

import re

from anbani.core.converter import data

DEFAULT_MISS = "[ა-ჰᲐ-ᲰႠ-Ⴠⴀ-ⴠa-zA-ZА-Яа-я]"


def count(text, miss=DEFAULT_MISS):
    """Raw occurrence count of each kept character (upper-cased)."""
    table = {}
    for ch in text.upper():
        if not re.search(miss, ch):
            continue
        table[ch] = table.get(ch, 0) + 1
    return table


def frequency(text, miss=DEFAULT_MISS):
    """Relative frequency of each kept character over the full string length."""
    upper = text.upper()
    length = len(upper)
    table = {}
    for ch in upper:
        if not re.search(miss, ch):
            continue
        table[ch] = table.get(ch, 0) + 1
    for key in table:
        table[key] /= length
    return table


def friedman(text, miss=DEFAULT_MISS):
    """Index of coincidence; 0 when fewer than two kept characters."""
    table = count(text, miss)
    total = sum(table.values())
    numerator = sum(n * (n - 1) for n in table.values())
    return numerator / (total * (total - 1)) if total > 1 else 0


def _numeral_map():
    values = data["alphabets"]["numeric"]
    table = {}
    for script in ("mkhedruli", "mtavruli", "asomtavruli", "nuskhuri"):
        for ch, v in zip(data["alphabets"][script], values):
            if ch and v.isdigit() and ch not in table:
                table[ch] = int(v)
    return table


_NUMERALS = _numeral_map()


def numeric_value(text):
    """Sum of the letters' numeral values (ჩქ -> 1600); everything else counts 0. Mirrors anbani.js numericValue."""
    return sum(_NUMERALS.get(ch, 0) for ch in text)
