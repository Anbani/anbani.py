import pandas as pd
import re

AMBIGRAM_BALANCED_PATH = "data/ambigram_nc5_len7.csv"
AMBIGRAM_ACCURATE_PATH = "data/ambigram_nc1_len10.csv"

extract_mapping = lambda df: df[~df.REDUNDANT][["MASKED", "NGRAM"]].values

ambigrams_balanced = extract_mapping(pd.read_csv(AMBIGRAM_BALANCED_PATH))
ambigrams_accurate = extract_mapping(pd.read_csv(AMBIGRAM_ACCURATE_PATH))


diphthong_mapping = [
    ("tsch", "ჭ"),
    ("tch", "ჭ"),
    ("ch", "ჩ"),
    ("sh", "შ"),
    ("dz", "ძ"),
    ("kh", "ხ"),
    ("th", "თ"),
    ("zh", "ჟ"),
    ("jh", "ჟ"),
    ("ph", "ფ"),
    ("gh", "ღ"),
    ("ts", "ც"),
]

common_errors = {
    "t" : ["ტ", "თ"],
    "p" : ["ფ", "პ"],
    "c" : ["ც", "წ"],
    "k" : ["ქ", "კ"],
    "j" : ["ჯ", "ჟ"],
    # "g" : ["გ", "ღ"],
}

letter_mapping = [    
    ('a', 'ა'),
    ('A', 'ა'),
    ('b', 'ბ'),
    ('B', 'ბ'),
    ('c', 'ც'),
    ('C', 'ჩ'),
    ('d', 'დ'),
    ('D', 'დ'),
    ('e', 'ე'),
    ('E', 'ე'),
    ('f', 'ფ'),
    ('F', 'ფ'),
    ('g', 'გ'),
    ('G', 'გ'),
    ('h', 'ჰ'),
    ('H', 'ჰ'),
    ('i', 'ი'),
    ('I', 'ი'),
    ('j', 'ჯ'),
    ('J', 'ჯ'),
    ('k', 'კ'),
    ('K', 'კ'),
    ('l', 'ლ'),
    ('L', 'ლ'),
    ('m', 'მ'),
    ('M', 'მ'),
    ('n', 'ნ'),
    ('N', 'ნ'),
    ('o', 'ო'),
    ('O', 'ო'),
    ('p', 'პ'),
    ('P', 'პ'),
    ('q', 'ქ'),
    ('Q', 'ქ'),
    ('r', 'რ'),
    ('R', 'ღ'),
    ('s', 'ს'),
    ('S', 'შ'),
    ('t', 'ტ'),
    ('T', 'თ'),
    ('u', 'უ'),
    ('U', 'უ'),
    ('v', 'ვ'),
    ('V', 'ვ'),
    ('w', 'წ'),
    ('W', 'ჭ'),
    ('x', 'ხ'),
    ('X', 'ხ'),
    ('y', 'ყ'),
    ('Y', 'ყ'),
    ('z', 'ზ'),
    ('Z', 'ძ')
]


def _transliterate_diphthongs(sentence):
    for dfrom, dto in diphthong_mapping:
        sentence = sentence.replace(dfrom, dto)

    return sentence


def _transliterate_letters(sentence, even_ambiguous=True):
    for mfrom, mto in letter_mapping:
        if not even_ambiguous and mfrom in common_errors:
            continue

        sentence = sentence.replace(mfrom, mto)

    return sentence


def _chevron_wrap(sentence):
    sentence = re.sub(r'\b(?:\w+-\w+|\w+)\b', lambda match: '<' + match.group() + '>', sentence)

    return sentence

def _chevron_unwrap(sentence):
    sentence = re.sub(r"<(\w+)>", r"\1", sentence)

    return sentence

def _transliterate_ngrams(sentence, ambigrams):
    for nfrom, nto in ambigrams:
        if nfrom in sentence:
            sentence = sentence.replace(nfrom, nto)

    return sentence


def georgianise_fast(sentence):
    """
    Fastest implementation of proper Georgianisation.
    """

    sentence = _transliterate_diphthongs(sentence)
    sentence = _transliterate_letters(sentence)

    return sentence


def georgianise_balanced(sentence):
    """
    Smarter than fastest, faster than Smartest. Uses 10K tokens.
    """
    
    sentence = _chevron_wrap(sentence)
    sentence = _transliterate_diphthongs(sentence)
    sentence = _transliterate_letters(sentence, even_ambiguous=False)
    sentence = _transliterate_ngrams(sentence, ambigrams=ambigrams_balanced)
    sentence = _chevron_unwrap(sentence)

    return sentence    


def georgianise_accurate(sentence):
    """
    Most accurate implementation of Georgianisation without applying comprehensive million row wordlist in brute force. Uses 50K tokens.
    """
    
    sentence = _chevron_wrap(sentence)
    sentence = _transliterate_diphthongs(sentence)
    sentence = _transliterate_letters(sentence, even_ambiguous=False)
    sentence = _transliterate_ngrams(sentence, ambigrams=ambigrams_accurate)
    sentence = _chevron_unwrap(sentence)

    return sentence    


def georgianise_custom(sentence, ambigrams_custom):
    """
    Custom Georgianisation for performance evaluation.
    """
    
    sentence = _chevron_wrap(sentence)
    sentence = _transliterate_diphthongs(sentence)
    sentence = _transliterate_letters(sentence, even_ambiguous=False)
    sentence = _transliterate_ngrams(sentence, ambigrams=ambigrams_custom)
    sentence = _chevron_unwrap(sentence)

    return sentence       
    
    

def georgianise(sentence, mode="accurate"):
    """
    Redeem others' qwerty sins.
    """

    if mode == "accurate":
        return georgianise_accurate(sentence)
    
    elif mode == "balanced":
        return georgianise_balanced(sentence)
    
    return georgianise_fast(sentence)

    

def latinise(sentence):
    """
    Blasphemous utility.
    """
    
    for latin, georgian_letters in common_errors.items():
        for letter in georgian_letters:
            sentence = sentence.replace(letter, latin)

    for dto, dfrom in diphthong_mapping:
        sentence = sentence.replace(dfrom, dto)
    
    for mto, mfrom in letter_mapping:
        sentence = sentence.replace(mfrom, mto)
    
    return sentence


