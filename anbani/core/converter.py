import hjson
import re

# Exact copy of the Javascript object from Anbani.JS for easier parallel development down the road
# .js because .json doesn't allow comments that would be parsable with hjson (human json)
data = hjson.loads(
    open("../anbani/data/letters.js").read().replace('export default ', '')
)

script_regex = {
    "mkhedruli": "[ა-ჿ]",
    "mtavruli": "[Ა-Ჿ]",
    "asomtavruli": "[Ⴀ-Ⴥ]",
    "nuskhuri": "[ⴀ-ⴥ]",
    "latin": "[a-zA-Z]",
    "cyrillic": "[А-Яа-я]"
}


# Single entrypoint for both bicameral and unicameral conversion
def convert(text, dir_from, dir_to):
    assert dir_from in [
        'mkhedruli',
        'mtavruli',
        'asomtavruli',
        'nuskhuri',
        'qwerty',
    ]

    if dir_to in [
        "anbanismtavruli",
        "shanidziseuli",
        "tfileliseuli",
        "khutsuri",
    ]:
        return convert_bicameral(text, dir_from, dir_to)
    else:
        return convert_unicameral(text, dir_from, dir_to)


# Source text script automatching, handy for automatic keyboards and etc
def interpret(text, dir_to):
    dir_from = classify_text(text)
    return convert(text, dir_from, dir_to)


# Loose script classifier
# TODO perhaps I should match with Anbani.JS vector matching or smth else entirely
def classify_text(text):
    for key in script_regex.keys():
        if re.compile(script_regex[key]).match(text):
            return key

    return 'unknown'


# Unicameral conversion
def convert_unicameral(text, dir_from, dir_to):
    return ''.join(map(
        lambda letter : letter_converter(
            letter, 
            dir_from, 
            dir_to
        ),
        text
    ))


# Bicameral conversion of Georgian texts. 
# "'anbanismtavruli' is just a temp name for now "- said George ages ago. 
# TODO come up with a better name hopefully with historical precedent. 
def convert_bicameral(text, dir_from, dir_to):
    rules = {
        "anbanismtavruli": {
            "upper": "asomtavruli",
            "lower": "mtavruli",
        },
        "tfileliseuli": {
            "upper": "mtavruli",
            "lower": "mkhedruli",
        },
        "shanidziseuli": {
            "upper": "asomtavruli",
            "lower": "mkhedruli",
        },
        "khutsuri": {
            "upper": "asomtavruli",
            "lower": "nuskhuri",
        },
    }

    upper_script = rules[dir_to]['upper']
    lower_script = rules[dir_to]['lower']

    # Convert first letter
    converted = letter_converter(
        text[0], dir_from, upper_script
    ) + convert_unicameral(text[1:], dir_from, lower_script)

    # Convert first letter after every sentence
    matched = re.finditer(r'[?.!჻]\s+[A-zა-ჿႠ-Ⴥⴀ-ⴥᲐ-Ჿ0-9]', converted)
    converted = list(converted)
    for match in matched:
        converted[match.end()-1] = letter_converter(
            converted[match.end()-1], lower_script, upper_script
        )

    # Convert first letter before every special letter
    matched = re.finditer(r'[ა-ჿႠ-Ⴥⴀ-ⴥᲐ-Ჿ]\'', ''.join(converted))
    for match in matched:
        converted[match.start()] = letter_converter(
            converted[match.start()], lower_script, upper_script
        )
        converted[match.start()+1] = ''

    return ''.join(converted)


def letter_converter(letter, dir_from, dir_to):
    try: return data['alphabets'][dir_to][
        data['alphabets'][dir_from].index(letter)
    ]
    except: return letter
