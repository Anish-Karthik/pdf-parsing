import re
from typing import Any, List, Tuple

import fitz

from utils.question import isanoption, isquestionare
from utils.util import is_underlined, get_lines


def extract_text_from_pdf(pdf_file: str) -> list:
    layout= []

    doc = fitz.open(pdf_file)

    for page in doc:
        layout.append("\n")
        hpos = set() 

        blocks = page.get_text("blocks") 
        for block in blocks:
            if isanoption(block): #check if it's an option
                hpos.add(block[0])
        prev = None
        for block in blocks:
            if prev == None:
                prev = block
            if not (isquestionare(hpos,block) and len(block[4]) < 200):
                if re.match(r"^\d{1,}\n",block[4]):
                    # print(block[4])
                    continue
                # remove starting dots
                if re.match(r"^\.{1,}",block[4]):
                    # print(block[4])
                    continue
                if re.match(r"Line\n5|(Line\n)",block[4]):
                    # print(block[4])
                    continue
                if re.match(r"(Unauthorized copying or reuse of any part of this page is illegal.)|(CO NTI N U E)|(STOP)", block[4]):
                    # print(block[4])
                    continue
                # if isnextqn(block,prev):
                #     layout.append("\n")
                layout.append(block[4])
                prev = block
    # print(len(layout))
    return layout

def underlined_text(pdf_path) -> List[List[Tuple[List[Any],str]]]:

    doc = fitz.open(pdf_path)

    underlined_sentences_all_pages = []
    
    for pgno,page in enumerate(doc):

        underlined_sentences = []
        underlined_sentence = []
        drawn_lines = get_lines(page)
        words = page.get_text("words")

        if pgno>10:
            prev_word_is_underlined = False
            qn_no=""
            for ind,w in enumerate(words):

                if is_underlined(w,drawn_lines):
                    if not prev_word_is_underlined:
                        if underlined_sentence != []:
                            underlined_sentences.append([underlined_sentence,qn_no])
                        underlined_sentence = []

                        qn_no = words[ind-1][4] if re.match(r'\d+',words[ind-1][4]) else ""
                    underlined_sentence.append(w)
                    # print(pgno,w[4])
                    prev_word_is_underlined = True
                else:
                    prev_word_is_underlined = False
            if len(underlined_sentence):
                underlined_sentences.append([underlined_sentence,qn_no])

        underlined_sentences_all_pages.append(underlined_sentences)

    return underlined_sentences_all_pages


def get_all_underlined_sentences(pdf_path: str) -> List[Tuple[List[Any], str]]:
    underlined_sentences_all_pages = underlined_text(pdf_path)
    all_underlined_sentences = []
    for underlined_sentence in underlined_sentences_all_pages:
        for sentence in underlined_sentence:
            all_underlined_sentences.append(sentence)
    return all_underlined_sentences

def get_all_underlined_sentences_only(all_underlined_sentences: List[Tuple[List[Any], str]]) -> List[Tuple[str, str]]:
    try:
        all_underlined_sentences_strings = []
        for sentence in all_underlined_sentences:
            qn_no = sentence[1]
            underlined_sentence = sentence[0]
            all_underlined_sentences_strings.append((" ".join([word[4] for word in underlined_sentence]), qn_no))
        return all_underlined_sentences_strings
    except Exception as e:
        print(e)
        raise Exception("Error in getting all underlined sentences only")