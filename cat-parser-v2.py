import os
import re

import fitz
import pandas as pd
from typing import List, Tuple, Any
from model import *
from catAnswerParser import get_all_answers

from utils.util import write_text_to_file, removenextline
from catQuestionParser import get_all_questions
def isStartOfPassage(block):
    return block[4].startswith("Instruction for questions ")

def isEndOfPassage(block):
    return block[4].startswith("Q.")

def parseQuestionNumber(block) -> list:
    tmp = [int(x) for x in re.findall(r"\d+", block[4])]
    if tmp is None:
        return []
    st, end = tmp
    return list(range(st, end+1))

def is_extra(block) -> bool:
    return "bodheeprep.com" in block[4]

def extract_passages_from_pdf(pdf_file: str):
    doc = fitz.open(pdf_file)
    passages = []
    isPassageStarted = False
    passage = []
    headers = []
    qnos = []
    for page in doc:
        blocks = page.get_text("blocks") 
        for block in blocks:
            if isPassageStarted:
                if isEndOfPassage(block):
                    isPassageStarted = False
                    passages.append("".join(passage))
                    passage = []
                    continue
                passage.append(block[4])
                continue
            if isStartOfPassage(block):
                headers.append(block[4])
                qnos.append(parseQuestionNumber(block))
                isPassageStarted = True
                continue
    return (headers,passages,qnos)

def isEndOfVARC(block):
    return block[4].startswith("Q.") and "17" in block[4]

def clean_text(text: str) -> str:
    text = re.sub(r"(\.|\?) ?\n", r"\1\n\t", text)
    text = re.sub(r"\n(?!\t)", r" ", text)
    return text

def split_passages(blocks) -> List[List[Any]]:
    passages: List[PassageTemp] = []
    isPassageStarted = False
    passage = []

    for block in blocks:
        if isEndOfVARC(block):
            print("End of VARC")
            print(len(passages))
            return passages
        if isPassageStarted:
            if isEndOfPassage(block):
                isPassageStarted = False
                passageText = clean_text("".join(passage))
                obj = PassageTemp(passageText, passage[0][4], parseQuestionNumber(passage[0]))
                passages.append(obj)
                passage = []
                continue
            passage.append(block[4])
            continue
        if isStartOfPassage(block):
            passage.append(block[4])
            isPassageStarted = True
            continue
    return passages

def parseQuestionNumber(txt) -> list:
    tmp = [int(x) for x in re.findall(r"\d+", txt)]
    if tmp is None or len(tmp) < 2:
        return []
    st, end = tmp
    return list(range(st, end+1))
class PassageTemp:
    def __init__(self, text: str, header: str, qnos: List[int]) -> None:
        self.text = text
        self.header = removenextline(header)
        self.qnos = qnos

def extract_comprehension(passage: PassageTemp, allQuestions: List[Question]) -> ReadingComprehension:
    return ReadingComprehension(Passage(passage.text), allQuestions[passage.qnos[0]-1:passage.qnos[-1]])

def get_each_lines(doc):
    lines = []
    for page in doc:
        line = []
        blocks = page.get_text("blocks")
        for block in blocks:
            if is_extra(block):
                continue
            block = list(block)
            line.append(block)
        lines.extend(line)
    print(len(lines))
    print(lines[0])
    return lines

def add_answers_to_questions(questions: List[Question], answers: List[Tuple[str,str]]) -> List[Question]:
    for i in range(len(questions)):
        questions[i].correct_option = answers[i][1]
    return questions


pdf_path = "input/cat/CAT 2021 Paper Slot 1.pdf"
answer_pdf_path = pdf_path

doc = fitz.open(pdf_path)
blocks = get_each_lines(doc)

allAnswers = get_all_answers(answer_pdf_path)
allQuestions = add_answers_to_questions(get_all_questions(pdf_path), allAnswers)


passages = split_passages(blocks)
comprehensions = [extract_comprehension(p, allQuestions) for p in passages]

write_text_to_file(json.dumps([c.to_json() for c in comprehensions], indent=2),"output/cat/CAT 2021 Paper Slot 1-passages.json")
print(len(passages))