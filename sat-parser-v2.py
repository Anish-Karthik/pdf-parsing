import os
import re
from typing import List
import json

import fitz
from utils.util import write_text_to_file
from answerParser import parse_answer

from satQuestionParser import *
from underline import *


def isStartOfPassage(block):
    isStart = bool(re.match(r'Questions \d*.*\d*', block[4]))
    return isStart


def fixBugForPassage4(txt):
    txt = txt.replace("\x14", "3")
    return txt.replace("\x15", "4")

def isEndOfPassage(block, qno=None):
    if qno:
        # get all the numbers in the text
        try:
            int(re.sub(r"[^\d]", "", block[4]))
        except ValueError:
            return False
        return int(re.sub(r"[^\d]", "", block[4])) == qno and re.search(r"^" + str(qno) + "", block[4])
    return block[0] in [338.7315979003906, 318.2538146972656, 39.872100830078125, 42.38639831542969, 68.39437866210938]


def parseQuestionNumber(txt) -> list:
    tmp = [int(x) for x in re.findall(r"\d+", txt)]
    if tmp is None or len(tmp) < 2:
        return []
    st, end = tmp
    return list(range(st, max(end, st + 10) + 1))


def is_extra_content_in_passage(block) -> bool:
    # isNum = bool(re.match(r"\d+\n",block[4]))
    # if not alphanumeric
    return (
        re.search(r"^Line\n5", block[4]) or
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

def get_reference_words(s):
    s = s.replace("\u201c", "“").replace("\u201d", "”")
    tmp = re.findall(r"\(“(.+)”\)",s)
    if len(tmp)==0:
        tmp = re.findall(r"“(.+)”",s)
    if len(tmp)!=0:
        words = re.split(r" \. \. \. ",tmp[0])
        start_words = words[0].split(" ")
        if len(words) == 1:
            return words[0].split(" "), None
        end_words = words[1].split(" ")
        return start_words, end_words
    return None, None

def match_words(words, passage_words):
    for i in range(len(passage_words) - len(words) + 1):
        m_words = [x.replace("\u201c", "“").replace("\u201d", "”").replace("“","").replace("”","") for x in passage_words[i:i+len(words)]]
        
        if [words[j] in m_words[j] for j in range(len(words))].count(True) == len(words):
            return i
    return None

def modify_single_reference(description: str, reference: Reference, comprehension: ReadingComprehension, debug =""):
    start_words, end_words = get_reference_words(description)
    passage_words = re.sub(r"\n", " ", comprehension.passage.passage).split()[reference.start_word:reference.end_word]
    del_start_ind = None
    del_end_ind = None
    print(description)
    if start_words is not None and end_words is not None:
        del_start_ind = match_words(start_words, passage_words)
        del_end_ind = match_words(end_words, passage_words[del_start_ind:])
        print(del_start_ind, del_end_ind)
    elif start_words is not None:
        del_start_ind = match_words(start_words, passage_words)
        del_end_ind = len(start_words) - 1
        print("v2",del_start_ind)
    else:
        print(f"Error{debug}: No words found")
    print(passage_words)
    print(start_words, end_words)
    print(reference.start_word, reference.end_word)
    if del_start_ind is not None and del_end_ind is not None:
        print("REf",del_start_ind, del_end_ind)
        print(reference.start_word+del_start_ind, reference.end_word-del_end_ind)
        reference.start_word += del_start_ind
        reference.end_word = reference.start_word+del_end_ind
    else:
        print(f"Error{debug}: words sequence not found")
    print("\n")

def modify_option_reference(option: Option, comprehension: ReadingComprehension, debug =""):
    return modify_single_reference(option.description, option.reference, comprehension, debug)

def modify_question_reference(question: Question, comprehension: ReadingComprehension, debug =""):
    for reference in question.references:
        modify_single_reference(question.description, reference, comprehension, debug)

def populate_reference(comprehension: ReadingComprehension):
    pattern1 = r"Lines\s+(\d+)\s*-\s*(\d+)" # option reference
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
                # work here match 1st word followed by \( and then match the last word before \)
                option.reference = (getReferences(comprehension.passage.passage, int(pattern1_match[0][0]), int(pattern1_match[0][-1])))
                # print the matched text by referencing the passage
                modify_option_reference(option, comprehension, "multiple")

            if len(pattern2_match):
                option.reference = (getReferences(comprehension.passage.passage, int(pattern2_match[0])))
                modify_option_reference(option, comprehension, "Single")

    # print(pattern1_match)
    # print(pattern2_match)
    return comprehension


def cleanPassage(passage: list) -> str:
    text = "".join([b[4] for b in passage]).strip()
    text = re.sub(r"\n+", "\n", text)
    text = re.sub(r"Line\n", "", text)
    text = re.sub(r"\d+\n", "", text)
    text = re.sub(r" +", " ", text)
    tmp = text.split("\t", 1)
    text = tmp[1] if len(tmp) > 1 else text
    text = re.sub(r"^\n", "", text)


    return text

def remove_line_no_from_passage(passage):
    isLineNoStarted = True
    curLine = 5

    new_passage = []
    
    for line in passage:
        if "Line" in line[4]:
            line[4] = re.sub(r"^Line ", "", line[4])
            isLineNoStarted = True
        if isLineNoStarted and re.search(rf"^{str(curLine)}", line[4]):
            line[4] = re.sub(rf"^{str(curLine)} ", "", line[4])
            curLine += 5
        new_passage.append(line)
    return new_passage

    
        


class PassageTemp:
    def __init__(self, text: str, header: str, qnos: List[int]) -> None:
        self.text = text
        self.header = remove_next_line(header)
        self.qnos = qnos


def format_passage(text):
    text = re.sub(r"(?<! )\n(?!\t)", " ", text)
    text = re.sub(r"(?<= )\n(?!\t)", "", text)
    return text

def extract_passages(blocks: List[Tuple[Any]]) -> ReadingComprehension:
    passage = []
    passageObjects: List[PassageTemp] = []
    header = blocks[0][4]
    
    qnos = parseQuestionNumber(fixBugForPassage4(header))
    
    tmp = None
    try:
        tmp = qnos[0]
    except IndexError:
        pass

    cur_passage_questions = get_questions_alter(blocks)
    for block in blocks[1:]:
        # print(block)
        block = list(block) + [False]
        if isEndOfPassage(block, tmp):

            passage = remove_line_no_from_passage(passage)
            # for i in passage:
            #     print(i[4])
            text = cleanPassage(passage)
            # print(text)
            
            passageObjects.append(PassageTemp(text, header, qnos))
            
            obj = populate_reference(
                ReadingComprehension(
                    Passage(text),
                    cur_passage_questions
                )
            )
            obj.passage.passage = format_passage(obj.passage.passage)
            return obj
        if is_extra_content_in_passage(block):
            continue
        if isStartOfParagraph(block, passage[-1] if len(passage) else None):
            block[4] = "\t" + block[4]
        passage.append(block)
    return None


def isStartOfWrittingComprehension(block):
    return bool(re.search(r"Section 2", block[4], re.IGNORECASE))


def split_passages(blocks) -> List[Tuple[List[str], bool]]:
    passages = []
    isPassageStarted = False
    passage_lines = []
    isWritingComprehension = 0
    all_comprehensions: List[ReadingComprehension] = []
    for i, block in enumerate(blocks):
        # print(block)
        if isStartOfWrittingComprehension(block):
            isWritingComprehension = 1
            continue
        if isStartOfPassage(block):
            # print(cur_passage_questions)
            isPassageStarted = True
            passage_lines.append((passages, isWritingComprehension == 2))
            passages = []
            if (isWritingComprehension == 1):
                isWritingComprehension = 2
        if isPassageStarted:
            if isSectionHeader(block):
                continue
            passages.append(block)
    passage_lines.append((passages, isWritingComprehension == 2))
    return passage_lines[1:]


def computeSection(passageObject, passageObjects, currentSection):
    try:
        if len(passageObjects) > 1:
            prevQuestionNumbers = passageObjects[-1].questionNumbers.split(",")
            currQuestionNumbers = passageObject.questionNumbers.split(",")
            if int(prevQuestionNumbers[-1]) > int(currQuestionNumbers[0]) and int(prevQuestionNumbers[-1]) > 0 and int(currQuestionNumbers[0]) > 0:
                currentSection += 1
    except Exception as e:
        print("Error in section assignment:", e)
    return currentSection


def get_all_words_for_underline(doc):
    all_words = []
    for pgno, page in enumerate(doc):
        words = page.get_text("words")
        for word in words:
            word = tuple(list(word) + [pgno])
            all_words.append(word)
    return all_words


all_words_index = 0


def extract_passages_writing_comprehension(blocks: List[Tuple[Any]]):
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
        if re.search(r"STOP", block[4]):
            break
        if is_extra_content_in_passage(block):
            continue
        if isStartOfParagraph(block, passage[-1] if len(passage) else None):
            block[4] = "\t" + block[4]
        passage.append(block)

    text = cleanPassage(passage)
    passageObjects.append(PassageTemp(text, header, qnos))

    obj = populate_reference(
        ReadingComprehension(
            Passage(text),
            cur_passage_questions
        )
    )
    doc_index, obj = underlined_references(
        obj,
        get_all_words_for_underline(doc),
        all_words_index,
        doc
    )
    all_words_index = doc_index
    obj.passage.passage = format_passage(obj.passage.passage)
    return obj


# def proccessPassageText(text):
#     text = re.sub(r"\n(?!\t)", " ", text)
#     text = re.sub(r"\n\t"," \n\t",text)
#     return text
#     # text = re.sub(r"\n", " ", text)
#     change = (len(re.findall(r" +", text))-1+len(re.findall(r" +\.", text))-1)
#     text = re.sub(r" +", " ", text)
#     text = re.sub(r" +\.", ".", text)
#     # remove \n that are not followed by a \t
#     text = re.sub(r"\n(?!\t)", " ", text)
#     if text.startswith("\n"):
#         text = text[1:]
#         change +=1
#     if not text.startswith("\t"):
#         text = "\t" + text
#         change -=1

#     print("change",change)
#     return text


pdf_paths = []
answer_pdf_paths = []

# pdf_paths.append("sat/inputPDF/SAT Practice Test 8.pdf")
# answer_pdf_paths.append("sat/inputPDF/SAT Practice Test 8 Answers.pdf")
for file in os.listdir("sat/inputPDF"):
    if file.endswith("Answers.pdf"):
        answer_pdf_paths.append("sat/inputPDF/" + file)
    elif file.endswith(".pdf"):
        pdf_paths.append("sat/inputPDF/" + file)

pdf_paths.sort()
answer_pdf_paths.sort()

files = zip(pdf_paths, answer_pdf_paths)
# print(pdf_paths, answer_pdf_paths)

for sample_paper, (pdf_path, answer_pdf_path) in enumerate(list(files), start=1):
    sample_paper = str(sample_paper)

    doc = fitz.open(pdf_path)
    blocks = get_each_lines(doc)

    all_comprehensions = []

    ans_doc = fitz.open(answer_pdf_path)
    answer_blocks = get_each_lines(ans_doc, True)
    all_answers = parse_answer(answer_blocks)

    passage_split = split_passages(blocks)
    print(len(passage_split))
    qno_cnt = 0
    for i, split in enumerate(passage_split):
        # print(split,"\n\n\n\n\n\n\n\n\n")
        split, isWritingComprehension = split
        # print(split, isWritingComprehension)
        comprehension = extract_passages(split) if not isWritingComprehension else extract_passages_writing_comprehension(split)
        if comprehension is not None:
            all_comprehensions.append(comprehension)
            for j, question in enumerate(comprehension.questions):
                question.correct_option = all_answers[qno_cnt].answer
                question.detailed_answer = all_answers[qno_cnt].detailed_solution
                question.qno = str(j + 1)
                qno_cnt += 1

    for i, obj in enumerate(all_comprehensions):
        write_text_to_file(json.dumps(obj.to_json(), indent=2), "sat/outputJSON/sat-sample-paper-" + sample_paper + f"-passage{i + 1}.json")

    # print(json.dumps([c.to_json() for c in all_comprehensions]))
    write_text_to_file(json.dumps([c.to_json() for c in all_comprehensions], indent=2), "debug/jsonOutput.json")
