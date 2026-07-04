"""Shared cross-language parity vectors.

spec/golden.json is byte-identical to anbani.js/spec/golden.json. Each vector
names a function (`id`), its `args`, and either an `expect` value or `raises`.
The expected values are generated from this library (the NLP source of truth)
and verified against anbani.js in its CI — the same file passing both suites is
the parity proof.
"""

import json
import os

import pytest

import anbani
from anbani.nlp import contractions, georgianisation, preprocessing

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(os.path.join(_ROOT, "spec", "golden.json"), encoding="utf-8") as _f:
    GOLDEN = json.load(_f)
TOL = GOLDEN["float_tolerance"]

# id -> language-native call (snake_case here, camelCase in the js consumer).
REGISTRY = {
    "core.convert": lambda a: anbani.convert(*a),
    "core.interpret": lambda a: anbani.interpret(*a),
    "core.classify": lambda a: anbani.classify_text(*a),
    "nlp.expand": lambda a: contractions.expand(*a),
    "nlp.expand_text": lambda a: contractions.expand_text(*a),
    "nlp.contract": lambda a: contractions.contract(*a),
    "nlp.contract_text": lambda a: contractions.contract_text(*a),
    "nlp.georgianise": lambda a: georgianisation.georgianise(*a),
    "nlp.latinise": lambda a: georgianisation.latinise(*a),
    "nlp.word_tokenize": lambda a: preprocessing.word_tokenize(*a),
    "nlp.sentence_tokenize": lambda a: preprocessing.sentence_tokenize(*a),
    "nlp.paragraph_tokenize": lambda a: preprocessing.paragraph_tokenize(*a),
    "nlp.cleanup": lambda a: preprocessing.cleanup(*a),
    "toolkit.count": lambda a: anbani.toolkit.count(*a),
    "toolkit.frequency": lambda a: anbani.toolkit.frequency(*a),
    "toolkit.friedman": lambda a: anbani.toolkit.friedman(*a),
}


def _almost_equal(a, b):
    if isinstance(a, bool) or isinstance(b, bool):
        return a is b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return abs(a - b) <= TOL
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(_almost_equal(x, y) for x, y in zip(a, b))
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(_almost_equal(a[k], b[k]) for k in a)
    return a == b


def test_registry_covers_every_id():
    for v in GOLDEN["vectors"]:
        assert v["id"] in REGISTRY, f"unregistered id: {v['id']}"


@pytest.mark.parametrize(
    "v",
    GOLDEN["vectors"],
    ids=[f"{i}-{v['id']}" for i, v in enumerate(GOLDEN["vectors"])],
)
def test_golden(v):
    fn = REGISTRY[v["id"]]
    if v.get("raises"):
        with pytest.raises(Exception):
            fn(v["args"])
    else:
        got = fn(v["args"])
        assert _almost_equal(got, v["expect"]), f"{v['id']}: got {got!r}, expect {v['expect']!r}"
