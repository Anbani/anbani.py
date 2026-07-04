from anbani.nlp.contractions import (
    cmap,
    contract,
    contract_text,
    expand,
    expand_text,
)


def test_cmap_loaded_from_csv():
    # Sanity: the stdlib-csv loader produced the same mapping pandas did.
    assert cmap["ა. შ."] == "ასე შემდეგ"
    assert len(cmap) > 300


def test_expand_known_contraction():
    assert expand("ა. შ.") == "ასე შემდეგ"


def test_expand_passthrough_unknown():
    assert expand("არააბრევიატურა") == "არააბრევიატურა"


def test_expand_text_replaces_contraction():
    assert expand_text("ვნახოთ ა. შ.") == "ვნახოთ ასე შემდეგ"


def test_expand_text_terminates_on_plain_text():
    # Regression: the old [ა-ჿ]+\. loop spun forever on any Georgian word
    # followed by a period that was not itself a contraction key.
    assert expand_text("ეს მარტივი ტექსტია") == "ეს მარტივი ტექსტია"


def test_contract_known_expansion():
    # Shared expansion resolves to the shortest contraction ("ა.შ." < "ა. შ.").
    assert contract("ასე შემდეგ") == "ა.შ."


def test_contract_passthrough_unknown():
    assert contract("არააბრევიატურა") == "არააბრევიატურა"


def test_contract_text_replaces_expansion():
    assert contract_text("ვნახოთ ასე შემდეგ") == "ვნახოთ ა.შ."


def test_contract_text_prefers_longest_expansion():
    longest = max(cmap.values(), key=len)
    assert contract_text(longest) == contract(longest)
