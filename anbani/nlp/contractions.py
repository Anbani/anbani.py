import csv
import os
from pathlib import Path

module_path = Path(__file__).parent.parent.absolute()

with open(
    os.path.join(module_path, "data/georgian_contractions.csv"),
    encoding="utf-8",
    newline="",
) as _f:
    cmap = {row["CONTRACTION"]: row["EXPANSION"] for row in csv.DictReader(_f)}

# Reverse direction (expansion -> contraction). Several contractions share one
# expansion (e.g. "ა. შ." and "ა.შ." both expand to "ასე შემდეგ"); keep the
# shortest contraction, with the string itself as a stable tie-break.
emap = {}
for _contraction, _expansion in cmap.items():
    _incumbent = emap.get(_expansion)
    if _incumbent is None or (len(_contraction), _contraction) < (len(_incumbent), _incumbent):
        emap[_expansion] = _contraction

# Some expansions are substrings of a longer expansion, so contract the longer
# phrase first.
_expansions_by_length = sorted(emap.items(), key=lambda kv: len(kv[0]), reverse=True)


def expand(word):
    # Just a wrapper around the contractions map
    return cmap.get(word, word)


def expand_text(text):
    # Sort contractions by length (longest first) to avoid partial matches
    sorted_contractions = sorted(cmap.keys(), key=len, reverse=True)
    for contraction in sorted_contractions:
        if contraction in text:
            text = text.replace(contraction, cmap[contraction])
    return text


def contract(phrase):
    # Inverse of expand()
    return emap.get(phrase, phrase)


def contract_text(text):
    # Inverse of expand_text(): replace known expansions with their contraction,
    # longest expansion first. Round-tripping expand_text() is not guaranteed.
    for expansion, contraction in _expansions_by_length:
        text = text.replace(expansion, contraction)
    return text
