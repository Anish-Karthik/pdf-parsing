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
    if re.match(r'^A Natural Synthetic ', block[4]) or re.match(r'^The Slums ', block[4]):
        return True
    return (
        re.match(r'Questions \d*.*\d*', block[4])
        or re.match(r'The following passage is from', block[4])
        or re.match(r'Passage [A-Z]\d*', block[4])
        or re.match(r'Two contemporary writers', block[4])
        or re.match(r'Below are \d+', block[4])
    )


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
    # if block[4].startswith(". "):
    #     block[7] = False
    #     return False
    block[7] = (
        (block[0] - prevBlock[0] > 12) or
        (prevBlock[7] and block[0] == prevBlock[0])
    )
    if block[7]:
        # print("bk",block)
        # print("pb",prevBlock)
        pass
    return block[7]


def getReferences(passageText: str, line_reference, startline: int, endLine=None) -> Reference:
    return get_reference_v2(passageText, line_reference,startline, endLine)
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

def get_reference_v2(passage, line_reference ,startline ,endline = None):
    words = passage.split()

    words_with_line_no = []
    for key, value in line_reference:
        line_words = value.split()
        words_with_line_no.extend([(key+1, word) for word in line_words])

    cur_word_ind = 0
    start_word_reference = None
    end_word_reference = None
    if not endline:
        endline = startline

    print(startline, endline)
    
    for key, word in words_with_line_no:
        print(word,words[cur_word_ind])
        if word == words[cur_word_ind]:
            if key == startline and start_word_reference is None:
                start_word_reference = cur_word_ind
            if key == endline:
                end_word_reference = cur_word_ind
            cur_word_ind += 1
        else:
            continue

    return Reference(start_word_reference, end_word_reference)

def populate_reference(comprehension: ReadingComprehension, line_reference):
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
            references.append(getReferences(comprehension.passage.passage, line_reference, int(pattern1_match[0][0]), int(pattern1_match[0][-1])))
        for startLine in pattern2_match:
            references.append(getReferences(comprehension.passage.passage, line_reference,int(startLine)))
        for [startLine1, startLine2] in pattern3_match:
            references.append(getReferences(comprehension.passage.passage, line_reference,int(startLine1)))
            references.append(getReferences(comprehension.passage.passage, line_reference,int(startLine2)))
        question.references = references

        # options
        for option in question.options:
            pattern1_match = re.findall(pattern1, option.description, re.IGNORECASE)
            pattern2_match = re.findall(pattern2, option.description, re.IGNORECASE)
            if len(pattern1_match):
                option.reference = (getReferences(comprehension.passage.passage, line_reference,int(pattern1_match[0][0]), int(pattern1_match[0][-1])))
            if len(pattern2_match):
                option.reference = (getReferences(comprehension.passage.passage, line_reference,int(pattern2_match[0])))

    # print(pattern1_match)
    # print(pattern2_match)
    return comprehension


def proccessPassageText(text):
    text = re.sub(r"\n+", "\n", text)
    text = re.sub(r" +", " ", text)
    text = re.sub(r"\s+\.", ".", text)
    # need to fix, but multiple lines parsing messed up everything
    text = re.sub(r"- *\n", "", text)
    # remove whitespace before and after \n or \n\t
    text = re.sub(r" *\n *", "\n", text)
    text = re.sub(r" *\n\t *", "\n\t", text)
    text = re.sub(r"(?<!\n\t)(Passage \d+)\n\t", r"\n\t\1\n\t", text)
    # remove \n that are not followed by a \t
    # text = re.sub(r"\n(?!\t)", " ", text)
    if text.startswith("\n"):
        text = text[1:]
    if not text.startswith("\t"):
        text = "\t" + text
    return text + "."


def cleanPassage(passage: list) -> str:
    for block in passage:
        block[4] = re.sub(r"^\(\d+\)", "", block[4])
        
    text = "\n".join([b[4] for b in passage]).strip()
    if re.search(r"Try\s+to\s+take\s+about\s+5\s+minutes\s+to\s+read\s+this\s+passage", text):
        text = re.split(r"Try\s+to\s+take\s+about\s+5\s+minutes\s+to\s+read\s+this\s+passage", text)[1]
        text = re.split(r"Time\s+Travel", text ,1)[1]
        text = re.split(r"With\s+each\s+of\s+these\s+questions", text, 1)[0].strip()
    text = re.split(r"Source:", text, 1)[0].strip()
    text = re.split(r"\d*\s*Citation:", text, 1)[0].strip()
    # remove any hyperlinks
    text = proccessPassageText(text)
    return text

def cleanPassagePostReference(text) -> str:
    text = re.sub(r"\n(?!\t)", " ", text)
    return text

def clean_block(block):
    block[4] = re.sub(r"\u2013", "-", block[4])
    return block


class PassageTemp:
    def __init__(self, text: str, header: str, qnos: List[int]) -> None:
        self.text = text
        self.header = remove_next_line(header)
        self.qnos = qnos

def create_line_references(blocks):
    line_references = list()
    for ind,block in enumerate(blocks):
        if re.match(r"^\((\d+)\)", block[4]):
            block[4] = re.sub(r"^\(\d+\)", "", block[4])
            count = 0
            if len(line_references) == 0:
                for it,temp in enumerate(blocks):
                    count+=1
                    if(temp == block):
                        break
                for it,temp in enumerate(blocks):
                    line_references.append((it - (count - 5),temp[4]))
                    if(temp == block):
                        break
                    
            else:
                for i in range(4,0,-1):
                    line_references.append((line_references[-1][0]+1,blocks[ind - i][4]))
                line_references.append((line_references[-1][0]+1,block[4]))

    return line_references
        

def extract_passages(blocks: List[Tuple[Any]]) -> ReadingComprehension:
    passage = []

    cur_passage_questions = get_questions_alter(blocks)
    buggy = 0
    for block in blocks[1:]:
        block = list(block) + [False]
        if re.match(r'MEDITATION I.', block[4]):
            buggy = 4
        if isEndOfPassage(block):
            if buggy > 0:
                buggy -= 1
                passage.append(block)
                continue
            
            line_references = create_line_references(passage)
            text = cleanPassage(passage)

            line_ref = []
            for i in line_references:
                line_ref.append(i[1])
                
            print("\n\n\n")
            min_l = min(len(text.split()), len((" ".join(line_ref)).split()))
            for i in range(min_l):
                if text.split()[i] != (" ".join(line_ref)).split()[i]:
                    print(i, text.split()[i], (" ".join(line_ref)).split()[i])
            
            obj = populate_reference(
                ReadingComprehension(
                    Passage(text),
                    cur_passage_questions,
                ),
                line_references
            )
            
            obj.passage.passage = cleanPassagePostReference(obj.passage.passage)
            return obj
        if is_extra(block):
            # print(block)
            continue
        if isStartOfParagraph(block, passage[-1] if len(passage) else None):
            block[4] = "\n\t" + block[4]
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
        # if not re.search(r"^Questions \d+.*\d+", block[4]) and re.search(r"Questions \d+.*\d+", block[4]):
        #     print("Error:", block)
        if isStartOfPassage(block):
            # print(cur_passage_questions)
            isPassageStarted = True
            passage_lines.append((passages, False))
            passages = []
        if isPassageStarted:
            if isSectionHeader(block):
                continue
            passages.append(block)
        if "ANSWERS EXPLAINED" in block[4]:
            break
    passage_lines.append((passages, False))
    return passage_lines[1:]


def fix_buggy_question(question: Question):
    # print(question.to_json())
    if re.search(r"\d+\.", question.description):
        question.qno = re.findall(r"\d+\.", question.description)[0].replace(".", "")
        question.description = re.split(r"\d+\.", question.description, 1)[1]
        # assign the correct qno
    # print(question.to_json())
    return question


def processQnos(comprehension: ReadingComprehension, all_comprehensions: List[ReadingComprehension]):
    st = set()
    for j, question in enumerate(comprehension.questions):
        if question.qno in st:
            # make this as a new Comprehension
            # remove the questions from the current comprehension
            # add the questions to the new comprehension
            # add the new comprehension to the all_comprehensions
            other_comprehension_questions = comprehension.questions[j:]
            comprehension.questions = comprehension.questions[:j]
            if len(other_comprehension_questions):
                other_comprehension_questions = processQnos(ReadingComprehension(Passage(None), other_comprehension_questions), all_comprehensions)
                all_comprehensions.append(other_comprehension_questions)
        st.add(question.qno)
    return comprehension


pdf_path = "baron/inputPDF/baron.pdf"
doc = fitz.open(pdf_path)
blocks = get_each_lines(doc)


all_comprehensions = []
all_answers = parse_answer(blocks)
all_words_for_underline = get_all_words_for_underline(doc)
all_words_index = 0

passage_split = split_passages(blocks)
print(len(passage_split))
print(len(all_answers))
# print("\n\n".join(str(x) for x in all_answers))
write_text_to_file(json.dumps([c.to_json() for c in all_answers], indent=2), "debug/jsonOutputAnswers.json")


qno_cnt = 0
print(len(passage_split))
debug_qno = []
for i, split in enumerate(passage_split):
    # print(split,"\n\n\n\n\n\n\n\n\n")
    split, isWritingComprehension = split
    comprehension = extract_passages(split) if not isWritingComprehension else extract_passages_writing_comprehension(split, all_words_for_underline)
    # remove the questions that are not having qnos

    if not comprehension:
        continue
    # comprehension.passage.passage = proccessPassageText(comprehension.passage.passage)
    comprehension.questions = [q for q in comprehension.questions if q.qno != ""]
    # fix buggy questions
    comprehension.questions = [q for q in comprehension.questions]
    all_comprehensions.append(comprehension)

    # write_text_to_file(json.dumps(comprehension.to_json(), indent=2), f"output/baron/baron-passage{len(all_comprehensions)}.json")
    each_qnos = []
    for j, question in enumerate(comprehension.questions):
        # try:
        if question.qno != all_answers[qno_cnt].question_number:
            print()
            print(json.dumps([(x.to_json()) for x in all_answers[qno_cnt - j - 1:len(comprehension.questions) + qno_cnt]], indent=2))
            raise Exception(f"Number mismatch at {qno_cnt}, Passage {len(all_comprehensions)}, A: {all_answers[qno_cnt].question_number}, Q: {question.qno}")
        question.correct_option = all_answers[qno_cnt].answer
        question.detailed_answer = all_answers[qno_cnt].detailed_solution
        # except Exception as e:
        #     print(e)
        #     print(f"Error at {qno_cnt}")
        # print(f"Question {question.qno} added")
        each_qnos.append(question.qno)
        qno_cnt += 1
    # check for repeating qnos from "1"
    processQnos(comprehension, all_comprehensions)
    debug_qno.append(each_qnos)
    # remove
    # write_text_to_file(json.dumps(comprehension.to_json(), indent=2), f"output/baron/baron-passage{len(all_comprehensions)}.json")


# print(qno_cnt)
# print(debug_qno)
# for i, x in enumerate(debug_qno, start=1):
#     print(i, x)
for i, obj in enumerate(all_comprehensions):
    write_text_to_file(json.dumps(obj.to_json(), indent=2), f"baron/outputJSON/baron-passage{i + 1}.json")


# print(json.dumps([c.to_json() for c in all_comprehensions]))
write_text_to_file(json.dumps([c.to_json() for c in all_comprehensions], indent=2), "debug/jsonOutput.json")
