import os
import re

import hjson

dirname = os.path.dirname(__file__)
datafilepath = os.path.realpath(os.path.join(dirname, "../data/letters.js"))

# Exact copy of the Javascript object from Anbani.JS for easier parallel
# development. It is a `.js` (not `.json`) file so it can carry comments, which
# hjson (human json) tolerates. Keep it byte-identical to
# anbani.js/src/lib/data.mjs so both libraries share a single source of truth.
with open(datafilepath, encoding="utf-8") as _f:
    data = hjson.loads(_f.read().replace("export default ", ""))

script_regex = {
    "mkhedruli": "[ა-ჿ]",
    "mtavruli": "[Ა-Ჿ]",
    "asomtavruli": "[Ⴀ-Ⴥ]",
    "nuskhuri": "[ⴀ-ⴥ]",
    "latin": "[a-zA-Z]",
    "cyrillic": "[А-Яа-я]",
}

# Scripts usable as a conversion *source* (i.e. that index 1:1 into the table).
VALID_SOURCES = ("mkhedruli", "mtavruli", "asomtavruli", "nuskhuri", "qwerty")

# Bicameral scripts pair an upper-case and a lower-case unicameral script.
BICAMERAL_RULES = {
    "sasataure":     {"upper": "asomtavruli", "lower": "mtavruli"},
    "tfileliseuli":  {"upper": "mtavruli",    "lower": "mkhedruli"},
    "shanidziseuli": {"upper": "asomtavruli", "lower": "mkhedruli"},
    "khutsuri":      {"upper": "asomtavruli", "lower": "nuskhuri"},
}

# Deprecated / classifier-side script names mapped to their canonical name.
SCRIPT_ALIASES = {
    "anbanismtavruli": "sasataure",  # historical placeholder, kept for back-compat
    "latin": "qwerty",               # what classify_text() reports for Latin input
}


# Single entrypoint for both bicameral and unicameral conversion
def convert(text, dir_from, dir_to):
    dir_from = SCRIPT_ALIASES.get(dir_from, dir_from)
    dir_to = SCRIPT_ALIASES.get(dir_to, dir_to)

    if dir_from not in VALID_SOURCES:
        raise ValueError(
            f"Unsupported source script {dir_from!r}; "
            f"expected one of {VALID_SOURCES}."
        )

    if dir_to in BICAMERAL_RULES:
        return convert_bicameral(text, dir_from, dir_to)

    if dir_to not in data["alphabets"]:
        raise ValueError(
            f"Unsupported target script {dir_to!r}; expected a bicameral script "
            f"{tuple(BICAMERAL_RULES)} or one of {tuple(data['alphabets'])}."
        )

    return convert_unicameral(text, dir_from, dir_to)


# Source-script automatching, handy for automatic keyboards etc.
def interpret(text, dir_to):
    dir_from = classify_text(text)
    if dir_from == "unknown":
        raise ValueError("Could not detect the source script of the given text.")
    return convert(text, dir_from, dir_to)


# Loose script classifier
def classify_text(text):
    for key, pattern in script_regex.items():
        # `search`, not `match`: the script may not start at position 0
        # (e.g. leading whitespace, quotes or digits).
        if re.search(pattern, text):
            return key
    return "unknown"


# Unicameral conversion
def convert_unicameral(text, dir_from, dir_to):
    return "".join(letter_converter(letter, dir_from, dir_to) for letter in text)


# Bicameral conversion of Georgian texts.
def convert_bicameral(text, dir_from, dir_to):
    if not text:
        return ""

    upper_script = BICAMERAL_RULES[dir_to]["upper"]
    lower_script = BICAMERAL_RULES[dir_to]["lower"]

    # First letter to the upper-case script, the remainder to the lower-case one
    converted = list(
        letter_converter(text[0], dir_from, upper_script)
        + convert_unicameral(text[1:], dir_from, lower_script)
    )

    # Upper-case the first letter after every sentence terminator
    for match in re.finditer(
        r"[?.!჻]\s+[A-Za-zა-ჿႠ-Ⴥⴀ-ⴥᲐ-Ჿ0-9]", "".join(converted)
    ):
        converted[match.end() - 1] = letter_converter(
            converted[match.end() - 1], lower_script, upper_script
        )

    # Upper-case a letter explicitly marked with a trailing apostrophe
    for match in re.finditer(r"[ა-ჿႠ-Ⴥⴀ-ⴥᲐ-Ჿ]'", "".join(converted)):
        converted[match.start()] = letter_converter(
            converted[match.start()], lower_script, upper_script
        )
        converted[match.start() + 1] = ""

    return "".join(converted)


def letter_converter(letter, dir_from, dir_to):
    try:
        return data["alphabets"][dir_to][data["alphabets"][dir_from].index(letter)]
    except ValueError:
        # Letter not present in the source alphabet (punctuation, spaces, …)
        return letter
