from anbani import lorem


def test_sentences_terminate_with_period():
    lorem.seed(1)
    s = lorem.sentences(6)
    assert s.endswith(".")
    # nwords words, punctuation attached — splitting on spaces yields nwords.
    assert len(s.rstrip(".").split()) == 6


def test_paragraphs_count():
    lorem.seed(2)
    p = lorem.paragraphs(4, 3)
    assert len([x for x in p.split("\n\n") if x]) == 3


def test_names_format():
    names = lorem.names(3)
    assert len(names) == 3
    assert all(len(n.split(" ")) == 2 for n in names)


def test_seed_is_reproducible():
    lorem.seed(123)
    a = lorem.sentences(5)
    lorem.seed(123)
    b = lorem.sentences(5)
    assert a == b


def test_load_wordlist_swaps_source():
    lorem.load_wordlist(["ტესტი"])
    try:
        assert lorem.random_word() == "ტესტი"
    finally:
        lorem.load_wordlist(lorem.VEFXWORDS)


def test_data_sizes():
    assert len(lorem.VEFXWORDS) == 100
    assert len(lorem.FNAMES) == 100
    assert len(lorem.LNAMES) == 100
