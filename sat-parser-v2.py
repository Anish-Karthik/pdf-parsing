import re
from typing import List
import json

import fitz
<<<<<<< HEAD
from utils.util import write_text_to_file
=======
from utils.util import write_text_to_file, isStartOfPassageHeaderBaron as isStartOfPassageHeader
>>>>>>> 714854eb988c9ca658cd948a77e9d2ffe913469a
from answerParser import parse_answer

from satQuestionParser import *
from underline import *

WRC_CNT = [0]
SMC_CNT = [0]

def isStartOfPassage(block):
<<<<<<< HEAD
    isStart = bool(re.match(r'Questions \d*.*\d*', block[4]))
    return isStart
=======
    if re.match(r'^A Natural Synthetic ', block[4]) or re.match(r'^The Slums ', block[4]):
        return True
    return (
        re.match(r'Questions \d*.*\d*', block[4])
        or re.match(r'The following passage is from', block[4])
        or re.match(r'Passage [A-Z]\d*', block[4])
        or re.match(r'Two contemporary writers', block[4])
        or re.match(r'Below are \d+', block[4])
        # or re.match(r'The following is an excerpt from', block[4])
    )


def isStartOfPassageInclusive(block):
    return (
        re.match(r'^A Natural Synthetic ', block[4])
        or re.match(r'^The Slums ', block[4])
        or re.match(r'^Microbiomes ', block[4])
        or re.match(r'^Time Travel ', block[4])
        or re.match(r'The following passage is from', block[4])
        or re.match(r'Two contemporary writers', block[4])
        or re.match(r'The following is an excerpt from', block[4])
    )

>>>>>>> 714854eb988c9ca658cd948a77e9d2ffe913469a


def fixBugForPassage4(txt):
    if "22-\x142" in txt:
        return txt.replace("22-\x142", "22-32")
    if "\x14\x14-\x152" in txt:
        return txt.replace("\x14\x14-\x152", "33-42")
    if "\x15\x14-52" in txt:
        return txt.replace("\x15\x14-52", "43-52")
    return txt


<<<<<<< HEAD
def isEndOfPassage(block, qno=None):
    if qno:
        # get all the numbers in the text
        try:
            int(re.sub(r"[^\d]", "", block[4]))
        except ValueError:
            return False
        return int(re.sub(r"[^\d]", "", block[4])) == qno and re.search(r"^" + str(qno) + "", block[4])
    return block[0] in [338.7315979003906, 318.2538146972656, 39.872100830078125, 42.38639831542969, 68.39437866210938]
=======
def isEndOfPassage(block):
    if re.search("With each of these questions, take these general steps", block[4]):
        return True
    return re.match(r"(?<!.)\d{1,2}\.", block[4])

>>>>>>> 714854eb988c9ca658cd948a77e9d2ffe913469a


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
<<<<<<< HEAD
    block[-1] = (
        (block[0] - prevBlock[0] > 12) or
        (prevBlock[-1] and block[0] == prevBlock[0])
=======
    # if block[4].startswith(". "):
    #     block[7] = False
    #     return False
    block[7] = (
        (block[0] - prevBlock[0] > 12) or
        (prevBlock[7] and block[0] == prevBlock[0])
>>>>>>> 714854eb988c9ca658cd948a77e9d2ffe913469a
    )
    if block[7]:
        # print("bk",block)
        # print("pb",prevBlock)
        pass
    return block[7]

<<<<<<< HEAD

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
=======

def getReferences(passageText: str, line_reference, startline: int, endLine=None) -> Reference:
    return get_reference_v2(passageText, line_reference, startline, endLine)


reference_count = 0
reference_found_count = 0


def get_reference_v2(passage, line_reference, startline, endline=None):
    global reference_count, reference_found_count
    words = passage.split()
    reference_count += 1

    words_with_line_no = []
    for key, value in line_reference:
        line_words = value.split()
        words_with_line_no.extend([(key, word) for word in line_words])

    cur_word_ind = 0
    start_word_reference = None
    end_word_reference = None
    if not endline:
        endline = startline

    cur_dic_ind = 0
    breaking_ind = None
    while cur_word_ind < len(words):
        if breaking_ind:
            cur_dic_ind = breaking_ind
            breaking_ind = None
        while cur_dic_ind < len(words_with_line_no):
            key = words_with_line_no[cur_dic_ind][0]
            word = words_with_line_no[cur_dic_ind][1]

            if word == words[cur_word_ind] or word in words[cur_word_ind] or words[cur_word_ind] in word:
                if key == startline and start_word_reference is None:
                    start_word_reference = cur_word_ind
                    reference_found_count += 1
                if key == endline:
                    end_word_reference = cur_word_ind
                cur_word_ind += 1
                if cur_word_ind == len(words):
                    break
            else:
                if not breaking_ind:
                    breaking_ind = cur_dic_ind
            cur_dic_ind += 1
        cur_word_ind += 1

    # if start_word_reference is not None and end_word_reference is not None:
    return Reference(start_word_reference, end_word_reference)

def get_reference_words(s):
    s = s.replace("\u201c", "“").replace("\u201d", "”")
    tmp = re.findall(r"\(“(.+)”\)",s)
    if len(tmp)==0:
        tmp = re.findall(r"“(.+)”",s)
    if len(tmp)!=0:
        words = re.split(r" \. ?\. ?\. ",tmp[0])
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

def modify_single_reference(description: str, reference: Reference, comprehension: ReadingComprehension, debug ="", cnt = 0):
    if cnt == 3:
        return False
    start_words, end_words = get_reference_words(description)
    f = False
    if not reference:
        # print(description)
        # print(f"Error{debug}: reference not found")
        return False
    if "paragraph" in description and (not reference.start_word or not reference.end_word):
        print("***********************DESCRIPTION***********\n",description,"\n")
        return False
    if not reference.start_word and not reference.end_word:
        print(description)
        print(f"Error{debug}: reference start and end word not found")
        WRC_CNT[0] += 1
        return False
    if not reference.start_word:
        # print(description)
        # print(f"Error{debug}: reference start word not found")

        return False
    if not reference.end_word:
        f = True
        print(description)
        # print(f"Error{debug}: reference end word not found")
        # reference.end_word = len(comprehension.passage.passage.split())
        return
    passage_words = re.sub(r"\n", " ", comprehension.passage.passage).split()[reference.start_word:reference.end_word]
    del_start_ind = None
    del_end_ind = None
    # print(description)
    if start_words is not None and end_words is not None:
        del_start_ind = match_words(start_words, passage_words)
        del_end_ind = match_words(end_words, passage_words[del_start_ind:])
        # print(del_start_ind, del_end_ind)
    elif start_words is not None:
        del_start_ind = match_words(start_words, passage_words)
        del_end_ind = len(start_words) - 1
        # print("v2",del_start_ind)
    else:
        if f:
            print(start_words, end_words)
            print(comprehension.passage.passage[reference.start_word:reference.end_word+1])
            print(f"Error{debug}: No words found")
            print("\n")
        f = False
        pass
    # print(passage_words)
    # print(start_words, end_words)
    # print(reference.start_word, reference.end_word)
    if del_start_ind is not None and del_end_ind is not None:
        # print("REf",del_start_ind, del_end_ind)
        # print(reference.start_word+del_start_ind, reference.end_word-del_end_ind)
        reference.start_word += del_start_ind
        reference.end_word = reference.start_word+del_end_ind
    else:
        if f: 
            print(comprehension.passage.passage[reference.start_word:reference.end_word+1])
            print(f"Error{debug}: words sequence not found")
            print("\n")
        pass
    return True
    # print("\n")

def modify_option_reference(option: Option, comprehension: ReadingComprehension, debug =""):
    return modify_single_reference(option.description, option.reference, comprehension, debug)

def modify_question_reference(question: Question, comprehension: ReadingComprehension, debug =""):
    for reference in question.references:
        modify_single_reference(question.description, reference, comprehension, debug)

def populate_reference(comprehension: ReadingComprehension, line_reference):
>>>>>>> 714854eb988c9ca658cd948a77e9d2ffe913469a
    pattern1 = r"Lines\s+(\d+)\s*-\s*(\d+)"
    pattern2 = r"Line\s+(\d+)"
    pattern3 = r"Lines\s+(\d+)\s*and\s*(\d+)"

    for question in comprehension.questions:
        pattern1_match = re.findall(pattern1, question.description, re.IGNORECASE)
        pattern2_match = re.findall(pattern2, question.description, re.IGNORECASE)
        pattern3_match = re.findall(pattern3, question.description, re.IGNORECASE)
        references = []

        if len(pattern1_match):
            references.append(getReferences(comprehension.passage.passage, line_reference, int(pattern1_match[0][0]), int(pattern1_match[0][-1])))
        for startLine in pattern2_match:
            references.append(getReferences(comprehension.passage.passage, line_reference, int(startLine)))
        for [startLine1, startLine2] in pattern3_match:
            references.append(getReferences(comprehension.passage.passage, line_reference, int(startLine1)))
            references.append(getReferences(comprehension.passage.passage, line_reference, int(startLine2)))
        question.references = references
<<<<<<< HEAD
=======
        modify_question_reference(question, comprehension, " question reference")
>>>>>>> 714854eb988c9ca658cd948a77e9d2ffe913469a

        # options
        for option in question.options:
            pattern1_match = re.findall(pattern1, option.description, re.IGNORECASE)
            pattern2_match = re.findall(pattern2, option.description, re.IGNORECASE)
            if len(pattern1_match):
                option.reference = (getReferences(comprehension.passage.passage, line_reference, int(pattern1_match[0][0]), int(pattern1_match[0][-1])))
                modify_option_reference(option, comprehension, " option multiple")
            if len(pattern2_match):
                option.reference = (getReferences(comprehension.passage.passage, line_reference, int(pattern2_match[0])))
                modify_option_reference(option, comprehension, " option single")

    # print(pattern1_match)
    # print(pattern2_match)
    return comprehension


<<<<<<< HEAD
def cleanPassage(passage: list) -> str:
    text = "".join([b[4] for b in passage]).strip()
    text = re.sub(r"\n+", "\n", text)
    tmp = text.split("\t", 1)
    text = tmp[1] if len(tmp) > 1 else text
    return text


=======
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
    return text


def cleanPassage(passage: list) -> str:
    for block in passage:
        block[4] = re.sub(r"^\(\d+\)", "", block[4])

    text = "\n".join([b[4] for b in passage]).strip()
    if re.search(r"Try\s+to\s+take\s+about\s+5\s+minutes\s+to\s+read\s+this\s+passage", text):
        text = re.split(r"Try\s+to\s+take\s+about\s+5\s+minutes\s+to\s+read\s+this\s+passage", text)[1]
        text = re.split(r"Time\s+Travel", text, 1)[1]
        text = re.split(r"With\s+each\s+of\s+these\s+questions", text, 1)[0].strip()
    text = re.split(r"Source:", text, 1)[0].strip()
    text = re.split(r"\d*\s*Citation:", text, 1)[0].strip()
    # remove any hyperlinks
    text = proccessPassageText(text)
    text = re.sub(r"\n(?!\t)", " ", text)
    return text


def cleanPassagePostReference(text) -> str:
    text = re.sub(r"\n(?!\t)", " ", text)
    return text


def clean_block(block):
    block[4] = re.sub(r"\u2013", "-", block[4])
    return block


>>>>>>> 714854eb988c9ca658cd948a77e9d2ffe913469a
class PassageTemp:
    def __init__(self, text: str, header: str, qnos: List[int]) -> None:
        self.text = text
        self.header = remove_next_line(header)
        self.qnos = qnos


<<<<<<< HEAD
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

=======
def create_line_references(blocks):
    line_references = list()
    for ind, block in enumerate(blocks):
        if re.match(r"^\((\d+)\)", block[4]):
            line_no = int(re.findall(r"^\((\d+)\)", block[4])[0])
            required_lines = line_no if not line_references else line_no - line_references[-1][0]

            block[4] = re.sub(r"^\(\d+\)", "", block[4])
            count = 0
            if len(line_references) == 0:
                for it, temp in enumerate(blocks):
                    count += 1
                    if (temp == block):
                        break
                for it, temp in enumerate(blocks):
                    line_references.append((it - (count - required_lines), temp[4]))
                    if (temp == block):
                        break

            else:
                for i in range(required_lines - 1, 0, -1):
                    line_references.append((line_references[-1][0] + 1, blocks[ind - i][4]))
                line_references.append((line_references[-1][0] + 1, block[4]))

    return line_references


def extract_passages(blocks: List[Tuple[Any]]) -> ReadingComprehension:
    passage = []
    headers = []
>>>>>>> 714854eb988c9ca658cd948a77e9d2ffe913469a
    cur_passage_questions = get_questions_alter(blocks)
    buggy = 0
    indent = 0
    for block in blocks[1:]:
        block = list(block) + [False]
        if re.match(r'MEDITATION I.', block[4]):
            buggy = 4
            indent = 4
        elif "Hemoglobinopathies" in block[4]:
            print("Buggy")
            buggy = 1
        elif "The earthquake in Haiti had a magnitude of" in block[4]:
            print("Buggy 2")
            buggy = 1
        if isEndOfPassage(block):
            if buggy > 0:
                buggy -= 1
                block[4] = ("\n\t" if indent else "") + block[4]
                indent -= 1
                passage.append(block)
                continue

            line_references = create_line_references(passage)
            text = cleanPassage(passage)
<<<<<<< HEAD
            passageObjects.append(PassageTemp(text, header, qnos))
=======

            line_ref = []
            for i in line_references:
                line_ref.append(i[1])
>>>>>>> 714854eb988c9ca658cd948a77e9d2ffe913469a

            obj = populate_reference(
                ReadingComprehension(
                    Passage(text),
                    cur_passage_questions,
                ),
                line_references
            )
            if len(headers):
                # TODO: process indent for headers
                obj.header = "".join([h[4] for h in headers])

            # obj.passage.passage = cleanPassagePostReference(obj.passage.passage)
            return obj
        if is_extra(block):
            continue
        if isStartOfParagraph(block, passage[-1] if len(passage) else None):
<<<<<<< HEAD
            passage.append(modifyBlockText(block, "\t" + block[4]))
        else:
            passage.append(block)
    return None


def isStartOfWrittingComprehension(block):
    return bool(re.search(r"WRITING AND LANGUAGE TEST", block[4], re.IGNORECASE))

=======
            block[4] = "\n\t" + block[4]
        if isStartOfPassageHeader(block):
            headers.append(block)
            continue
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

>>>>>>> 714854eb988c9ca658cd948a77e9d2ffe913469a

def split_passages(blocks) -> List[Tuple[List[str], bool]]:
    passages = []
    isPassageStarted = False
    passage_lines = []
<<<<<<< HEAD
    isWritingComprehension = 0
    all_comprehensions: List[ReadingComprehension] = []
=======
>>>>>>> 714854eb988c9ca658cd948a77e9d2ffe913469a
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
<<<<<<< HEAD
            if (isWritingComprehension == 1):
                isWritingComprehension = 2
=======
            if isStartOfPassageInclusive(block):
                passages = [block]
>>>>>>> 714854eb988c9ca658cd948a77e9d2ffe913469a
        if isPassageStarted:
            if isStartOfPassageInclusive(block):
                passages = [block]
            if isSectionHeader(block):
                continue
            passages.append(block)
        if "ANSWERS EXPLAINED" in block[4]:
            break
    passage_lines.append((passages, False))
    return passage_lines[1:]

<<<<<<< HEAD

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
        if is_extra(block):
            continue
        if isStartOfParagraph(block, passage[-1] if len(passage) else None):
            passage.append(modifyBlockText(block, "\t" + block[4]))
        else:
            passage.append(block)

    text = cleanPassage(passage)
    passageObjects.append(PassageTemp(text, header, qnos))

    obj = populate_reference(
        ReadingComprehension(
            Passage(text),
            cur_passage_questions
        )
    )
    doc_index,obj = underlined_references(
        obj,
        get_all_words_for_underline(doc),
        all_words_index,
        doc
    )
    all_words_index = doc_index
    return obj


sample_paper = "8"

pdf_path = "input/sat/SAT Practice Test 1.pdf"
=======

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
>>>>>>> 714854eb988c9ca658cd948a77e9d2ffe913469a
doc = fitz.open(pdf_path)
blocks = get_each_lines(doc)


all_comprehensions = []
<<<<<<< HEAD
# all_answers = SolutionParsing.extract_text_with_ocr(answer_pdf_path)
answer_pdf_path = "input/sat-answers/SAT Practice Test 1.pdf"
ans_doc = fitz.open(answer_pdf_path)
answer_blocks = get_each_lines(ans_doc, True)
all_answers = parse_answer(answer_blocks)

passage_split = split_passages(blocks)
# print(len(passage_split))
=======
all_answers = parse_answer(blocks)
all_words_for_underline = get_all_words_for_underline(doc)
all_words_index = 0

passage_split = split_passages(blocks)
print(len(passage_split))
print(len(all_answers))
# print("\n\n".join(str(x) for x in all_answers))
write_text_to_file(json.dumps([c.to_json() for c in all_answers], indent=2), "debug/jsonOutputAnswers.json")


>>>>>>> 714854eb988c9ca658cd948a77e9d2ffe913469a
qno_cnt = 0
print(len(passage_split))
debug_qno = []
for i, split in enumerate(passage_split):
    split, isWritingComprehension = split
    comprehension = extract_passages(split)
    # remove the questions that are not having qnos

    if not comprehension:
        continue
    # comprehension.passage.passage = proccessPassageText(comprehension.passage.passage)
    comprehension.questions = [q for q in comprehension.questions if q.qno != ""]
    # fix buggy questions
    comprehension.questions = [q for q in comprehension.questions]
    all_comprehensions.append(comprehension)

    each_qnos = []
    for j, question in enumerate(comprehension.questions):

        if question.qno != all_answers[qno_cnt].question_number:
            print("wrong answer matched:", question.qno, all_answers[qno_cnt].question_number)
        question.correct_option = all_answers[qno_cnt].answer
        question.detailed_answer = all_answers[qno_cnt].detailed_solution

        each_qnos.append(question.qno)
        qno_cnt += 1
    # check for repeating qnos from "1"
    processQnos(comprehension, all_comprehensions)
    debug_qno.append(each_qnos)

for i, obj in enumerate(all_comprehensions):
<<<<<<< HEAD
    write_text_to_file(json.dumps(obj.to_json(), indent=2), "output/SATJson/sat-sample-paper-" + sample_paper + f"-passage{i + 1}.json")


# print(json.dumps([c.to_json() for c in all_comprehensions]))
write_text_to_file(json.dumps([c.to_json() for c in all_comprehensions], indent=2), "debug/jsonOutput.json")
=======
    write_text_to_file(json.dumps(obj.to_json(), indent=2), f"baron/outputJSON/baron-passage{i + 1}.json")

write_text_to_file(json.dumps([c.to_json() for c in all_comprehensions], indent=2), "debug/jsonOutput.json")
# print(reference_found_count,reference_count)

print(WRC_CNT, SMC_CNT)
>>>>>>> 714854eb988c9ca658cd948a77e9d2ffe913469a
