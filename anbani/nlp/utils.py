import pandas as pd
from tqdm import tqdm
import re
from collections import defaultdict
import fitz

def ebook2text(path):
    try:
        doc = fitz.open(path)
        n_pages = doc.page_count
        
        text = ""
        
        for p in range(n_pages):
            text += doc.load_page(p).get_text()
        
        # Replace hyphen-newline to connect words
        text = text.replace('-\n', '') # 002D
        text = text.replace('‐\n', '') # 2010
        text = text.replace('‑\n', '') # 2011
        text = text.replace('‒\n', '') # 2012
        text = text.replace('–\n', '') # 2013
        text = text.replace('—\n', '') # 2014
        text = text.replace('―\n', '') # 2015
        text = text.replace('−\n', '') # 2212
        text = text.replace('֊\n', '') # 058A
        text = text.replace('⁻\n', '') # 207B
        text = text.replace('₋\n', '') # 208B
        text = text.replace('⸺\n', '') # 2E3A	
        text = text.replace('⸻\n', '') # 2E3B	
        text = text.replace('﹘\n', '') # FES8
        text = text.replace('－\n', '') # FF0D	
        text = text.replace('﹣\n', '') # FE63

        # Replace paragraph and random new lines
        text = text.replace('\n', ' ')
    except Exception as e:
        return 'Error: ' + str(e)

    return text
