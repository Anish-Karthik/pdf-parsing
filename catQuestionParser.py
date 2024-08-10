import fitz
import re
import pandas as pd
from model import *
def is_option(block):
    return re.search(r"\[\d+\]",block[4]) or re.search(r"(?<!.)[A-D]\.",block[4])

def is_first_option(block):
    return re.search(r"\[1\]",block[4]) or re.search(r"(?<!.)A\.",block[4])

def is_qn(block):
    return re.search(r"Q.( ){0,1}\d+\)",block[4])

def remove_next_line(text):
    return re.sub(r"\n"," ",text)

def remove_qn_no(text):
    text = re.sub(r"Q.( ){0,1}","",text)
    return re.sub(r"\)","",text)

def is_extra(block) -> bool:
    return re.search(r"bodheeprep", block[4], re.IGNORECASE) or re.search(r"\d* *CAT \d+ QUESTION", block[4], re.IGNORECASE)


def get_qns(doc):
    qns = []
    lines = []
    for page in doc:
        blocks = page.get_text("blocks")
        for block in blocks:
            if is_extra(block):
                continue
            lines.append(block)

    for ind,line in enumerate(lines):
        if is_first_option(line):
            qn = [[],[]]
            i = ind-1
            while not is_qn(lines[i]):
                if "https:" not in lines[i][4] and "CAT 2023 QUESTION PAPER WITH ANSWER KEYS (SLOT 01)" not in lines[i][4]: 
                    qn[1].append(lines[i])
                i-=1
            else:
                qn[0] = lines[i]
            
            qn[1].reverse()
            qns.append(qn)
    return qns

            
def get_options(pdf_path,doc):
    options = ""
    seperated_options = []

    for page in doc:
        blocks = page.get_text("blocks")
        for block in blocks:
            if is_extra(block):
                continue
            if is_option(block):
                options += block[4]
    
    if "2023" in pdf_path:
        options = re.split(r"(?<!.)[A-D]\.",options) #for format A. B. C. D.
    else:
        options = re.split(r"\[\d+\]",options) #for format [1] [2] [3] [4]
    
    for i in range(1,len(options),4):
        if len(options) - i < 4:
            seperated_options.append(options[i:])
        else:
            seperated_options.append(options[i:i+4])
    return seperated_options
        
def get_all_questions(pdf_path): 
    final_text = []
    doc = fitz.open(pdf_path)

    options = get_options(pdf_path,doc)
    qns = get_qns(doc)
    
    for i in range(16):
        each_text = []
        # each_text.append(pdf_path[:-4])
        # each_text.append("1")
        each_text.append(remove_qn_no(remove_next_line(qns[i][0][4])))
        # print(qns[i][0][4])
        desc = ""
        for qn in qns[i][1]:
            desc += remove_next_line(qn[4])
            # print(qn[4],end=" ")
        each_text.append(remove_next_line(desc))
        # print()
        for option in options[i]:
            each_text.append(remove_next_line(option))
            # print(option)
        final_text.append(each_text)
        # print()
    question_arr = []
    for i in final_text:       
        options = [Option(option.strip()) for option in i[2:]]
        question = Question(i[0], i[1].strip(), options)
        question_arr.append(question)
    return question_arr