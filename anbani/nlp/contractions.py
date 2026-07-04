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

# Replace longest contractions first so that e.g. "ა.ს.ს.რ." is handled before
# the shorter "ა." that it contains.
_contractions_by_length = sorted(cmap.items(), key=lambda kv: len(kv[0]), reverse=True)


def expand(word):
    # Just a wrapper around the contractions map
    return cmap.get(word, word)


def expand_text(text):
    # Replace every known contraction with its expansion.
    for contraction, expansion in _contractions_by_length:
        text = text.replace(contraction, expansion)

    return text
