# AnbaniPy

Georgian Python toolkit for NLP, Transliteration and more. Partially based on [anbani.js](https://github.com/anbani/anbani.js).  

## Install

```bash
pip install anbani
```

## Quickstart

Transliteration example:

```python
from anbani.core.converter import convert, interpret

interpret("გამარჯობა", "asomtavruli")

# 'ႢႠႫႠႰႿႭႡႠ'
```

Convert ebooks with qwerty encoding to unicode Mkhedruli:

```python
from anbani.nlp.utils import ebook2text
from anbani.core.converter import classify_text
from anbani.core.converter import convert

text = ebook2text("/home/george/Dev/georgian-text-corpus/sources/mylibrary/raw/files/ჩარლზ დიკენსი - დევიდ კოპერფილდი.pdf")
print(text[:300])

print(classify_text(text))

print(convert(text, "qwerty", "mkhedruli")[:300])

# Carlz dikensi daviT koperfildi Tavi pirveli dabadeba me viqnebi gmiri Cemive sakuTari Tavgadasavlisa Tu sxva...

# latin

# ჩარლზ დიკენსი დავით კოპერფილდი თავი პირველი დაბადება მე ვიქნები გმირი ჩემივე საკუთარი თავგადასავლისა თუ სხვა...
```

Expand contractions:

```python
from anbani.nlp.contractions import expand_text

text = "ილია ჭავჭავაძე (დ. 8 ნოემბერი, 1837, სოფელი ყვარელი — გ. 12 სექტემბერი, 1907, წიწამური)"

print(text)
print(expand_text(text))

# ილია ჭავჭავაძე (დ. 8 ნოემბერი, 1837, სოფელი ყვარელი — გ. 12 სექტემბერი, 1907, წიწამური)
# ილია ჭავჭავაძე (დაბადება 8 ნოემბერი, 1837, სოფელი ყვარელი — გარდაცვალება 12 სექტემბერი, 1907, წიწამური)

```

## To-Do

Feel free to fork this repo!  

- [x] Tokenizer
- [x] Transliteration 
- [x] Expand contractions
- [x] ebook2pdf converter
- [ ] Stemmer
- [ ] Lemmatizer
- [ ] Stopwords


## Resources used

- http://www.nplg.gov.ge/civil/statiebi/wignebi/qartul_enis_marTlwera/qartul_enis_marTlwera_tavi-12.htm
- http://www.nplg.gov.ge/civil/upload/Semokleba.htm