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
