from anbani import toolkit


def test_count_uppercases_and_filters():
    # Mkhedruli is upper-cased to Mtavruli; spaces are dropped.
    assert toolkit.count("აბ ბ") == {"Ა": 1, "Ბ": 2}


def test_frequency_denominator_includes_filtered_chars():
    # "აბ ბ" has length 4 (space counted), so Ბ appears 2/4.
    freq = toolkit.frequency("აბ ბ")
    assert freq == {"Ა": 0.25, "Ბ": 0.5}


def test_friedman_zero_for_short_input():
    assert toolkit.friedman("") == 0
    assert toolkit.friedman("ა") == 0


def test_friedman_index_of_coincidence():
    # "ააბ" -> counts {Ა:2, Ბ:1}, total 3: (2*1 + 0) / (3*2) = 1/3.
    assert abs(toolkit.friedman("ააბ") - (1 / 3)) < 1e-12


def test_custom_miss_filter():
    # Restrict to Latin only; Georgian is dropped.
    assert toolkit.count("abაბ", miss="[a-zA-Z]") == {"A": 1, "B": 1}
