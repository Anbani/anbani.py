from anbani.nlp.preprocessing import (
    cleanup,
    nested_tokenize_by_separators,
    paragraph_tokenize,
    sentence_tokenize,
    word_tokenize,
)


def test_word_tokenize_strips_non_georgian():
    assert word_tokenize("გამარჯობა, მსოფლიო!") == ["გამარჯობა", "მსოფლიო"]


def test_word_tokenize_lowercases_mtavruli():
    # str.lower() maps Mtavruli -> Mkhedruli
    assert word_tokenize("ᲒᲐᲛᲐᲠᲯᲝᲑᲐ") == ["გამარჯობა"]


def test_sentence_tokenize_nested():
    assert sentence_tokenize("გ ა. ბ გ.") == [["გ", "ა"], ["ბ", "გ"]]


def test_sentence_tokenize_question_and_exclamation_split():
    # ? and ! are normalised to sentence terminators
    assert sentence_tokenize("ა ბ! გ დ?") == [["ა", "ბ"], ["გ", "დ"]]


def test_paragraph_tokenize_splits_on_newline():
    assert paragraph_tokenize("გ ა\nბ გ") == [["გ", "ა"], ["ბ", "გ"]]


def test_cleanup_collapses_whitespace_keeps_punctuation():
    assert cleanup("გ,  ა!") == "გ, ა!"


def test_nested_tokenize_is_separator_generic():
    assert nested_tokenize_by_separators("a b\nc", "\n", " ") == [["a", "b"], ["c"]]
    assert nested_tokenize_by_separators("", "\n", " ") == []
