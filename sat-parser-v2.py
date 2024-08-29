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
    return (bool(re.match(r'(?<!.)Questions\s\d+.\d+', block[4])) or
            bool(re.match(r'(?<!.)Questions\s\d+\sand\s\d+', block[4])) or
            bool(re.match(r'For each of the following questions', block[4])))


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


def isEndOfReadingComprehension(block):
    return "STOP" in block[4]


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


def is_subheading(line):
    return re.match(r"Passage \d", line) and len(line) < 14


def get_line_reference_index(lines):
    return len(" ".join(lines).split())


def getReferences(passageText: str, startline: int, endLine=None) -> Reference:
    # print(passageText[:100])
    if not endLine:
        endLine = startline
    startline -= 1
    endLine -= 1

    lines = passageText.split("\n")

    for line_no, line in enumerate(lines):
        if is_subheading(line):
            if line_no < startline:
                startline += 1
            if line_no < endLine:
                endLine += 1

    # print("REFERENCES number", startline, endLine)
    startWord = get_line_reference_index(lines[:startline])
    if endLine == len(lines):
        endWord = get_line_reference_index(lines)
    endWord = get_line_reference_index(lines[:endLine + 1])
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
    text = "".join([re.sub(r"\.\n", ".\n\t", b[4]) for b in passage]).strip()
    text = re.sub(r"\n+", "\n", text)
    return proccessPassageText(text)


def clean_block(block):
    block[4] = re.sub(r"\u2013", "-", block[4])
    return block


def get_header_index(blocks):
    header_prefixes = [
        "The following passage",
        "Each of the following sentences",
        "In this excerpt",
        "In the following excerpt",
        "The following excerpt",
        "In the following passage",
        "The book from which the following passage",
        "Taken from the writings of",
        "These passages are portraits of",
        "Both passages relate to",
        "African elephants now are an",
        "Passage 1 is an excerpt",
        "Pablo Picasso was probably the",
        "Largely unexplored, the canopy or treetop",
        "The style of the renowned modern artist",
    ]
    for index, block in enumerate(blocks[:5]):
        for prefix in header_prefixes:
            if prefix in block[4]:
                return index


class PassageTemp:
    def __init__(self, text: str, header: str, qnos: List[int]) -> None:
        self.text = text
        self.header = remove_next_line(header)
        self.qnos = qnos


def get_subheading_references(passage_text) -> List[Reference]:
    passage_list = passage_text.split("\n")
    # print(len(" ".join(passage_list).split()))
    subheading_references = []
    for ind, line in enumerate(passage_list):
        if is_subheading(line):
            start_ind = get_line_reference_index(passage_list[:ind])
            for word in line.split():
                if word == "Passage":
                    break
                start_ind += 1
            subheading_references.append(Reference(start_ind, start_ind + 1))

    return subheading_references


def extract_passages(blocks: List[Tuple[Any]]) -> ReadingComprehension:
    passage = []

    start_index = 1
    header_index = get_header_index(blocks)
    header = None
    if header_index:
        header = blocks[header_index][4]
        start_index = header_index + 1

    cur_passage_questions = get_questions_alter(blocks)
    for block in blocks[start_index:]:
        block = list(block) + [False]
        if isEndOfPassage(block):
            if header:
                header = proccessPassageText(header)

            obj = ReadingComprehension(
                Passage("".join([b[4] for b in passage]).strip()),
                cur_passage_questions,
                header=header
            )

            obj.subheading_references = get_subheading_references(obj.passage.passage)
            obj = populate_reference(obj)
            obj.passage.passage = cleanPassage(passage)
            return obj
        if is_extra(block):
            # print(block)
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


def split_passages(blocks) -> List[Tuple[List[str], bool]]:
    passages = []
    isPassageStarted = False
    passage_lines = []
    for i, block in enumerate(blocks):
        block = clean_block(block)
        if isEndOfReadingComprehension(block):
            isPassageStarted = False
            if len(passages) > 0:
                passage_lines.append((passages, False))
                passages = []
            continue
        if isStartOfPassage(block):
            isPassageStarted = True
            if len(passages) > 0:
                passage_lines.append((passages, False))
                passages = []
        if isPassageStarted:
            if isSectionHeader(block):
                continue
            passages.append(block)
    if len(passages) > 0:
        passage_lines.append((passages, False))
    return passage_lines


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


def mergeReferencesWithPassage(readingComprehension: ReadingComprehension):
    passage_links = []
    for qid, question in enumerate(readingComprehension.questions):
        for opt_index, option in enumerate(question.options):
            if option.reference is not None and option.reference.start_word is not None and option.reference.end_word is not None:
                passage_links.append(PassageLink(question=qid, option=opt_index, word_index=option.reference.start_word, is_start=True, is_header=False))
                passage_links.append(PassageLink(question=qid, option=opt_index, word_index=option.reference.end_word + 1, is_start=False, is_header=False))

        for reference in question.references:
            passage_links.append(PassageLink(question=qid, option=None, word_index=reference.start_word, is_start=True, is_header=False))
            passage_links.append(PassageLink(question=qid, option=None, word_index=reference.end_word + 1, is_start=False, is_header=False))

    for ref in readingComprehension.subheading_references:
        passage_links.append(PassageLink(question=qid, option=None, word_index=ref.start_word, is_start=True, is_header=True))
        passage_links.append(PassageLink(question=qid, option=None, word_index=ref.end_word + 1, is_start=False, is_header=True))

    passage_links = sorted(passage_links, key=lambda link: link.word_index)
    passage_links.reverse()

    passage_words = readingComprehension.passage.passage.split(" ")
    for link in passage_links:
        passage_words.insert(link.word_index, link.link())

    readingComprehension.passage.passage = " ".join(passage_words)


pdf_path = "baron/inputPDF/SAT WorkBook.pdf"
doc = fitz.open(pdf_path)
blocks = get_each_lines(doc)

all_comprehensions = []
all_answers = parse_answer(doc)
print(len(all_answers))
all_words_for_underline = get_all_words_for_underline(doc)
all_words_index = 0

passage_split = split_passages(blocks)
# print(len(passage_split))

qno_cnt = 0
qns = []
for i, split in enumerate(passage_split):
    split, isWritingComprehension = split
    comprehension = extract_passages(split)

    if comprehension is not None:
        all_comprehensions.append(comprehension)
        for j, question in enumerate(comprehension.questions):
            qns.append(question.qno)
            question.correct_option = all_answers[qno_cnt].answer
            question.detailed_answer = all_answers[qno_cnt].detailed_solution
            qno_cnt += 1

        mergeReferencesWithPassage(comprehension)
# print(qno_cnt)
# print(qns)

for i, obj in enumerate(all_comprehensions):
    write_text_to_file(json.dumps(obj.to_json(), indent=2), f"baron/outputJSON/barron-workbook-passage{i + 1}.json")


# print(json.dumps([c.to_json() for c in all_comprehensions]))
write_text_to_file(json.dumps([c.to_json() for c in all_comprehensions], indent=2), "debug/jsonOutput.json")
