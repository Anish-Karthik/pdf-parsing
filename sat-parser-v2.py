import os
import re

import fitz
import pandas as pd
from utils.util import write_text_to_file


def isStartOfPassage(block):
    return bool(re.match(r'Questions \d*-\d*', block[4]))

def isEndOfPassage(block, qno = None):
    if qno:
        return re.search(r"^"+str(qno), block[4])
    return block[0] in [338.7315979003906, 318.2538146972656, 39.872100830078125, 42.38639831542969]

def parseQuestionNumber(block) -> list:
    tmp = [int(x) for x in re.findall(r"\d+", block[4])]
    if tmp is None:
        return []
    st, end = tmp
    return list(range(st, end+1))

def is_extra(block) -> bool:
    # isNum = bool(re.match(r"\d+\n",block[4]))
    # if not alphanumeric
    return (
      re.search(r"Line\n5?",block[4]) or
      re.search(r"Unauthorized copying", block[4]) or
      re.search(r"CO NTI N U E", block[4]) or
      re.search(r"STOP", block[4]) or
      not re.search(r'[a-zA-Z]', block[4])
    )


def extract_passages_from_pdf(pdf_file: str = "input/sat/SAT Practice Test 1.pdf"):
    doc = fitz.open(pdf_file)
    passages = []
    isPassageStarted = False
    passage = []
    headers = []
    qnos = []
    
    for page in doc:
        blocks = page.get_text("blocks") 
        for block in blocks:
            print(block)
            
            if isPassageStarted:
                if isEndOfPassage(block, qnos[-1][0]):
                    isPassageStarted = False
                    passages.append("".join(passage))
                    passage = []
                    continue
                if is_extra(block):
                    continue
                passage.append(block[4])
                continue
            if isStartOfPassage(block):
                headers.append(block[4])
                qnos.append(parseQuestionNumber(block))
                isPassageStarted = True
                continue
    print(passages)
    write_text_to_file("\n\n\n\n".join(passages), "debug/SAT1tempPassages.txt")
    print(qnos)
    return (headers,passages,qnos)

extract_passages_from_pdf()