from anbani.nlp.contractions import (
    cmap,
    contract,
    contract_text,
    emap,
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


def test_expand_text_respects_word_boundaries():
    # "ჰა" (-> "ჰექტარი") is the only dotless contraction key; it must fire as
    # a standalone token but never inside a word.
    assert expand_text("ჰაერი") == "ჰაერი"
    assert expand_text("100 ჰა მიწა") == "100 ჰექტარი მიწა"


def test_expand_text_does_not_rescan_replacements():
    # Single-pass: an inserted expansion must not itself be re-expanded
    # (e.g. the "ჰა" inside "ბუხჰალტერია").
    assert expand_text("ბუხჰალტ.") == cmap["ბუხჰალტ."]


def test_contract_text_respects_word_boundaries():
    # "თავი" is an expansion, but it must not fire inside "თავისუფალი".
    assert contract_text("თავისუფალი ქვეყანა") == "თავისუფალი ქვეყანა"


def test_contract_text_matches_contract_for_every_expansion():
    # Full invariant: contracting a bare expansion always yields exactly its
    # contraction — catches chained-replacement bugs (e.g. "ათასწლეული" must
    # become "ათასწ.", not "ათ.წ." via a second pass over the insertion).
    for expansion, contraction in emap.items():
        assert contract_text(expansion) == contraction


def test_expand_text_matches_expand_for_every_contraction():
    for contraction, expansion in cmap.items():
        assert expand_text(contraction) == expansion
