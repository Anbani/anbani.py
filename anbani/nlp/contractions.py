import csv
import os
import re
from pathlib import Path

module_path = Path(__file__).parent.parent.absolute()

with open(
    os.path.join(module_path, "data/georgian_contractions.csv"),
    encoding="utf-8",
    newline="",
) as _f:
    cmap = {row["CONTRACTION"]: row["EXPANSION"] for row in csv.DictReader(_f)}


def _reverse_map(cmap):
    # Expansion -> contraction. Several contractions share one expansion
    # (e.g. "ა. შ." and "ა.შ." both expand to "ასე შემდეგ"); keep the shortest
    # contraction, with the string itself as a stable tie-break.
    emap = {}
    for contraction, expansion in cmap.items():
        incumbent = emap.get(expansion)
        if incumbent is None or (len(contraction), contraction) < (len(incumbent), incumbent):
            emap[expansion] = contraction
    return emap


emap = _reverse_map(cmap)


def _replacer(mapping):
    # Single-pass substitution: keys are matched longest-first (so "ა.ს.ს.რ."
    # wins over its prefix "ა.") and only at Georgian word boundaries (so keys
    # never fire inside a word, e.g. "ჰა" in "ჰაერი"). One pass also means an
    # inserted replacement is never itself re-replaced.
    keys = sorted(mapping, key=len, reverse=True)
    pattern = re.compile(
        "(?<![ა-ჿ])(?:" + "|".join(map(re.escape, keys)) + ")(?![ა-ჿ])"
    )
    return lambda text: pattern.sub(lambda m: mapping[m.group(0)], text)


_expand_replacer = _replacer(cmap)
_contract_replacer = _replacer(emap)


def expand(word):
    # Just a wrapper around the contractions map
    return cmap.get(word, word)


def expand_text(text):
    # Replace every known contraction with its expansion.
    return _expand_replacer(text)


def contract(phrase):
    # Inverse of expand()
    return emap.get(phrase, phrase)


def contract_text(text):
    # Inverse of expand_text(): every known expansion is abbreviated, so prose
    # that happens to contain one (e.g. a bare "ახალი") gets contracted too.
    return _contract_replacer(text)
