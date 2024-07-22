import os
import re

import fitz
import pandas as pd
from utils.util import write_text_to_file


def isStartOfPassage(block):
    return re.search(r'Questions \d+.\d+', block[4])

def isEndOfPassage(block, qno = None):
#     if qno:
#         return re.search(r"^"+str(qno), block[4])
#     print(block[4])
    return block[0] in [10.040771484375]

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


def extract_passages_from_pdf(pdf_file: str):
    doc = fitz.open(pdf_file)
    passages = []
    isPassageStarted = False
    passage = []
    headers = []
    qnos = []
    
    for page in doc[14:118]:
        blocks = page.get_text("blocks") 
        for block in blocks:
            print(block)
            
            if isPassageStarted:
                if isEndOfPassage(block):
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
    write_text_to_file("\n\n\n\n".join(passages), "debug/baron1tempPassages.txt")
    print(qnos)
    print(headers)
    return (headers,passages,qnos)

extract_passages_from_pdf("input/baron.pdf")