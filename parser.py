import fitz
import re
from utils.question import isanoption, isquestionare, isnextqn

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