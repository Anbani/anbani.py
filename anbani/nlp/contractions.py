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
