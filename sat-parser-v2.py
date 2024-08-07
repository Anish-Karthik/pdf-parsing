import re
from typing import List
import json

import fitz
from utils.util import write_text_to_file
from answerSat import AnswerTmp, SolutionParsing
from answerParser import parse_answer

from satQuestionParser import *
from underline import *


def isStartOfPassage(block):
    return bool(re.match(r'(?<!.)Passage\s\d+A?\s*$', block[4]))


def fixBugForPassage4(txt):
    if "22-\x142" in txt:
        return txt.replace("22-\x142", "22-32")
    if "\x14\x14-\x152" in txt:
        return txt.replace("\x14\x14-\x152", "33-42")
    if "\x15\x14-52" in txt:
        return txt.replace("\x15\x14-52", "43-52")
    return txt


def isEndOfPassage(block):
    return re.match(r"(?<!.)\d+\.", block[4])


def parseQuestionNumber(txt) -> list:
    tmp = [int(x) for x in re.findall(r"\d+", txt)]
    if tmp is None or len(tmp) < 2:
        return []
    st, end = tmp
    return list(range(st, max(end, st + 10) + 1))


def is_extra(block) -> bool:
    # isNum = bool(re.match(r"\d+\n",block[4]))
    # if not alphanumeric
    return (
        re.search(r"Line\n5?", block[4]) or
        re.search(r"Unauthorized copying", block[4]) or
        re.search(r"CO NTI N U E", block[4]) or
        re.search(r"STOP", block[4]) or
        re.search(r"SAT.*PRACTICE\n", block[4]) or
        not re.search(r'[a-zA-Z]', block[4])
    )


def isSectionHeader(block) -> bool:
    return (
        re.search(r"1\n1\n", block[4]) or
        re.search(r"2\n2\n", block[4])
    )


def isStartOfParagraph(block, prevBlock=None):
    if not prevBlock:
        return False
    # compare x values
    block[-1] = (
        (block[0] - prevBlock[0] > 12) or
        (prevBlock[-1] and block[0] == prevBlock[0])
    )
    return block[-1]


def modifyBlockText(block, txt):
    return (*block[:4], txt, *block[5:])


def getReferences(passageText: str, startline: int, endLine=None) -> Reference:
    # print(passageText[:100])
    lines = passageText.split("\n")
    startline -= 1
    if endLine:
        endLine -= 1
    # print("REFERENCES number", startline, endLine)
    startWord = len(" ".join(lines[:startline]).split())
    if not endLine:
        endLine = startline
    if endLine == len(lines):
        endWord = len(" ".join(lines).split())
    endWord = len(" ".join(lines[:endLine + 1]).split())
    # print(re.sub(r"\n", " ", passageText).split()[startWord:endWord])
    # print("References:", startWord, endWord)
    return Reference(startWord, endWord)


def populate_reference(comprehension: ReadingComprehension):
    pattern1 = r"Lines\s+(\d+)\s*-\s*(\d+)"
    pattern2 = r"Line\s+(\d+)"
    pattern3 = r"Lines\s+(\d+)\s*and\s*(\d+)"

    for question in comprehension.questions:
        pattern1_match = re.findall(pattern1, question.description, re.IGNORECASE)
        pattern2_match = re.findall(pattern2, question.description, re.IGNORECASE)
        pattern3_match = re.findall(pattern3, question.description, re.IGNORECASE)
        references = []
        # print(comprehension.passage.passage[:100])
        # print(question.description)
        # print(pattern1_match)
        # print(pattern2_match)
        if len(pattern1_match):
            references.append(getReferences(comprehension.passage.passage, int(pattern1_match[0][0]), int(pattern1_match[0][-1])))
        for startLine in pattern2_match:
            references.append(getReferences(comprehension.passage.passage, int(startLine)))
        for [startLine1, startLine2] in pattern3_match:
            references.append(getReferences(comprehension.passage.passage, int(startLine1)))
            references.append(getReferences(comprehension.passage.passage, int(startLine2)))
        question.references = references

        # options
        for option in question.options:
            pattern1_match = re.findall(pattern1, option.description, re.IGNORECASE)
            pattern2_match = re.findall(pattern2, option.description, re.IGNORECASE)
            if len(pattern1_match):
                option.reference = (getReferences(comprehension.passage.passage, int(pattern1_match[0][0]), int(pattern1_match[0][-1])))
            if len(pattern2_match):
                option.reference = (getReferences(comprehension.passage.passage, int(pattern2_match[0])))

    # print(pattern1_match)
    # print(pattern2_match)
    return comprehension


def cleanPassage(passage: list) -> str:
    text = "".join([b[4] for b in passage]).strip()
    text = re.sub(r"\n+", "\n", text)
    return text


def clean_block(block):
    block[4] = re.sub(r"\u2013", "-", block[4])
    return block


class PassageTemp:
    def __init__(self, text: str, header: str, qnos: List[int]) -> None:
        self.text = text
        self.header = remove_next_line(header)
        self.qnos = qnos


def extract_passages(blocks: List[Tuple[Any]]) -> ReadingComprehension:
    passage = []

    cur_passage_questions = get_questions_alter(blocks)
    for block in blocks[1:]:
        block = list(block) + [False]
        if isEndOfPassage(block):
            text = cleanPassage(passage)

            obj = populate_reference(
                ReadingComprehension(
                    Passage(text),
                    cur_passage_questions
                )
            )
            return obj
        if is_extra(block):
            print(block)
            continue
        if isStartOfParagraph(block, passage[-1] if len(passage) else None):
            passage.append(modifyBlockText(block, "\t" + block[4]))
        else:
            passage.append(block)

    return None


def get_all_words_for_underline(doc):
    all_words = []
    for pgno, page in enumerate(doc):
        words = page.get_text("words")
        for word in words:
            word = tuple(list(word) + [pgno])
            all_words.append(word)
    return all_words


def extract_passages_writing_comprehension(blocks: List[Tuple[Any]], all_words):
    global all_words_index
    passage = []
    passageObjects: List[PassageTemp] = []
    header = blocks[0][4]
    qnos = parseQuestionNumber(fixBugForPassage4(header))

    cur_passage_questions = get_questions_alter(blocks)
    for block in blocks[1:]:
        if (not block[7]):
            continue
        block = list(block) + [False]
        # not isLeft
        # print(block)
        if re.search(r"STOP", block[4]) or isEndOfPassage(block):
            break
        if is_extra(block):
            continue
        if isStartOfParagraph(block, passage[-1] if len(passage) else None):
            passage.append(modifyBlockText(block, "\t" + block[4]))
        else:
            passage.append(block)

    text = cleanPassage(passage)
    passageObjects.append(PassageTemp(text, header, qnos))

    last_index, obj = underlined_references(
        ReadingComprehension(Passage(text), cur_passage_questions), all_words, all_words_index, doc)

    all_words_index = last_index

    return obj


def split_passages(blocks) -> List[Tuple[List[str], bool]]:
    passages = []
    isPassageStarted = False
    passage_lines = []
    for i, block in enumerate(blocks):
        # print(block)
        block = clean_block(block)
        if isStartOfPassage(block):
            # print(cur_passage_questions)
            isPassageStarted = True
            passage_lines.append((passages, len(passage_lines) > 22))
            passages = []
        if isPassageStarted:
            if isSectionHeader(block):
                continue
            passages.append(block)
    passage_lines.append((passages, len(passage_lines)))
    return passage_lines[1:]

def proccessPassageText(text):
    # text = re.sub(r"\n", " ", text)
    text = re.sub(r" +", " ", text)
    text = re.sub(r" +\.", ".", text)
    # remove \n that are not followed by a \t
    text = re.sub(r"\n(?!\t)", " ", text)
    if not text.startswith("\t"):
        text = "\t" + text
    if text.endswith("\n\t"):
        text = text[:-2]
    return text


pdf_path = "mcgrawhill/inputPDF/Mcgraw Hill 6 Tests.pdf"
doc = fitz.open(pdf_path)
blocks = get_each_lines(doc)


all_comprehensions = []
all_answers = parse_answer(blocks)
all_words_for_underline = get_all_words_for_underline(doc)
all_words_index = 0

passage_split = split_passages(blocks)[:44]
print(len(passage_split))

qno_cnt = 0
for i, split in enumerate(passage_split):
    # print(split,"\n\n\n\n\n\n\n\n\n")
    split, isWritingComprehension = split
    comprehension = extract_passages(split) if not isWritingComprehension else extract_passages_writing_comprehension(split, all_words_for_underline)
    if comprehension is not None:
        comprehension.passage.passage = proccessPassageText(comprehension.passage.passage)
        all_comprehensions.append(comprehension)
        for j, question in enumerate(comprehension.questions):
            question.correct_option = all_answers[qno_cnt].answer
            question.detailed_answer = all_answers[qno_cnt].detailed_solution
            qno_cnt += 1

for i, obj in enumerate(all_comprehensions):
    write_text_to_file(json.dumps(obj.to_json(), indent=2), f"mcgrawhill/outputJSON/mcgrawhill-2-passage-{i + 1}.json")


# print(json.dumps([c.to_json() for c in all_comprehensions]))
write_text_to_file(json.dumps([c.to_json() for c in all_comprehensions], indent=2), "debug/jsonOutput.json")
