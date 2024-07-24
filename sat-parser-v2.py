import re
from  typing import List
import json

import fitz
from utils.util import write_text_to_file
from answerSat import AnswerTmp, SolutionParsing

from satQuestionParser import *


def isStartOfPassage(block):
    isStart =  bool(re.match(r'Questions \d*.*\d*', block[4]))
    return isStart

def fixBugForPassage4(txt):
    if "22-\x142" in txt:
        return txt.replace("22-\x142", "22-32")
    if "\x14\x14-\x152" in txt:
        return txt.replace("\x14\x14-\x152", "33-42")
    if "\x15\x14-52" in txt:
        return txt.replace("\x15\x14-52", "43-52")
    return txt

def isEndOfPassage(block, qno = None):
    if qno:
        # get all the numbers in the text
        try: int(re.sub(r"[^\d]", "", block[4]))
        except ValueError: return False
        return int(re.sub(r"[^\d]", "", block[4])) == qno and re.search(r"^"+str(qno)+"", block[4])
    return block[0] in [338.7315979003906, 318.2538146972656, 39.872100830078125, 42.38639831542969, 68.39437866210938]

def parseQuestionNumber(txt) -> list:
    tmp = [int(x) for x in re.findall(r"\d+", txt)]
    if tmp is None or len(tmp) < 2:
        return []
    st, end = tmp
    return list(range(st, max(end,st+10)+1))


def is_extra(block) -> bool:
    # isNum = bool(re.match(r"\d+\n",block[4]))
    # if not alphanumeric
    return (
        re.search(r"Line\n5?",block[4]) or
        re.search(r"Unauthorized copying", block[4]) or
        re.search(r"CO NTI N U E", block[4]) or
        re.search(r"STOP", block[4]) or
        re.search(r"SAT.*PRACTICE\n", block[4]) or
        not re.search(r'[a-zA-Z]', block[4])
    )
def isSectionHeader(block) -> bool:
    return (
        re.search(r"1\n1\n",block[4]) or
        re.search(r"2\n2\n", block[4]) 
    )

def isStartOfParagraph(block, prevBlock = None):
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

def getReferences(passageText: str, startline: int, endLine = None) -> Reference:
    print(passageText[:100])
    lines = passageText.split("\n")
    startline -= 1
    if endLine:
        endLine -= 1
    print("REFERENCES number", startline, endLine)
    startWord = len(" ".join(lines[:startline]).split())
    if not endLine:
        endLine = startline
    if endLine == len(lines):
        endWord = len(" ".join(lines).split())
    endWord = len(" ".join(lines[:endLine + 1]).split())
    print(re.sub(r"\n", " ", passageText).split()[startWord:endWord])
    print("References:", startWord, endWord)
    return Reference(startWord, endWord)

def cleanPassage(passage: list) -> str:
    text = "".join([b[4] for b in passage]).strip()
    text = re.sub(r"\n+", "\n", text)
    tmp =  text.split("\t", 1)
    text = tmp[1] if len(tmp) > 1 else text
    return text

class PassageTemp:
    def __init__(self, text: str, header: str, qnos: List[int]) -> None:
        self.text = text
        self.header = remove_next_line(header)
        self.qnos = qnos

def extract_passages_from_pdf(blocks):
    passages = []
    isPassageStarted = False
    passage = []
    headers = []
    qnos = []
    passageObjects: List[PassageTemp] = []
    for block in blocks:
        # print(block)
        block = list(block) + [False]
        if isPassageStarted:
            tmp = None
            try: tmp = qnos[-1][0] 
            except IndexError: pass
            if isSectionHeader(block):
                print("Section header found")
                continue
            if isEndOfPassage(block, tmp):
                isPassageStarted = False
                text = cleanPassage(passage)
                passages.append(text)
                passageObjects.append(PassageTemp(text, headers[-1], qnos[-1]))
                # getReferences(text, 5)
                # getReferences(text, 7,8)
                # getReferences(text, 34,37)
                # getReferences(text, len(text.split("\n")))
                # getReferences(text, len(text.split("\n"))-2, len(text.split("\n")))
                passage = []
                continue
            if is_extra(block):
                continue
            if isStartOfParagraph(block, passage[-1] if len(passage) else None):
                passage.append(modifyBlockText(block, "\t"+block[4]))
            else:
                passage.append(block)
            continue
        if isStartOfPassage(block):
            headers.append(block[4])
            qnos.append(parseQuestionNumber(fixBugForPassage4(block[4])))
            isPassageStarted = True
            continue
    # print(passages)
    write_text_to_file("\n\n\n\n".join(passages), "debug/SAT1tempPassages.txt")
    print(qnos)
    print(headers)
    
    return passageObjects

def computeSection(passageObject, passageObjects, currentSection):
    try:
        if len(passageObjects) > 1:
            prevQuestionNumbers = passageObjects[-1].questionNumbers.split(",")
            currQuestionNumbers = passageObject.questionNumbers.split(",")
            if int(prevQuestionNumbers[-1]) > int(currQuestionNumbers[0]) and int(prevQuestionNumbers[-1]) > 0 and int(currQuestionNumbers[0]) > 0:
                currentSection += 1
    except Exception as e:
        print("Error in section assignment:",e)
    return currentSection

def populate_reference(comprehension: ReadingComprehension):
    pattern1 = r"Lines\s+(\d+)\s*-\s*(\d+)"
    pattern2 = r"Line\s+(\d+)"
    pattern3 = r"Lines\s+(\d+)\s*and\s*(\d+)"
    
    for question in comprehension.questions:
        pattern1_match = re.findall(pattern1, question.description, re.IGNORECASE)
        pattern2_match = re.findall(pattern2, question.description, re.IGNORECASE)
        pattern3_match = re.findall(pattern3, question.description, re.IGNORECASE)
        references = []
        print(comprehension.passage.passage[:100])
        print(question.description)
        print(pattern1_match)
        print(pattern2_match)
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

    print(pattern1_match)
    print(pattern2_match)
    return comprehension

pdf_path = "input/sat/SAT Practice Test 1.pdf"
answer_pdf_path = "input/sat-answers/SAT Practice Test 1.pdf"
doc = fitz.open(pdf_path)
blocks = get_each_lines(doc)

all_passages = extract_passages_from_pdf(blocks)
all_answers = SolutionParsing.extract_text_with_ocr()
all_questions = get_questions_alter(blocks)

print(len(all_answers))
print(len(all_questions))

all_comprehensions: List[ReadingComprehension] = []

section = 0
# error on all_pass 5
for i, passage in enumerate(all_passages[:5]):
    # write_text_to_file(, f"debug/SAT1Passage{i+1}.txt")
    if passage.qnos[0] == 1:
        section += 1
    for ind, q in enumerate(passage.qnos, start=1):
        all_questions[q-1].qno = ind
        answerTmpObj = all_answers[q-1]
        if answerTmpObj.answer:
            all_questions[q-1].correct_option = answerTmpObj.answer
            all_questions[q-1].detailed_answer = answerTmpObj.detailed_solution
    obj = populate_reference(ReadingComprehension(
        Passage(passage.text), 
        all_questions[passage.qnos[0]-1: passage.qnos[-1]],
        section,
    ))
    all_comprehensions.append(obj)
    write_text_to_file(json.dumps(obj.to_json(), indent=2), f"output/SATJson/sat-sample-paper-1-passage{i+1}.json")


# print(json.dumps([c.to_json() for c in all_comprehensions]))
write_text_to_file(json.dumps([c.to_json() for c in all_comprehensions], indent=2), "debug/jsonOutput.json")

# all_options = get_references(all_options)

# for op in all_options:
#     print(op)

# [qtxt,qno, references]
    


# all_questions = get_references(all_questions)



# for qn in all_questions[:50]:
#     print(qn.description)
#     populate_reference(qn)



# if __name__ == '__main__':
#     finalDataFrame = pd.DataFrame(columns=["Sample paper", "Section", "Question no","Passage", "Header", "Source details","Character Metadata","Word Metadata"])

#     pdf_file_path = ""
#     file_list = os.listdir("input/sat")

#     # Iterate over each file
#     for paperNumber, file_name in enumerate(file_list, start=1):
#         if file_name.endswith(".pdf"):
#             pdf_file_path = os.path.join("input/sat", file_name)
#         try:
#             [headers,passages,qnos] = extract_passages_from_pdf(pdf_file_path)
#             passageObjects = []
#             section = 1
#             for i, passage in enumerate(passages):
#                 # section assignment
#                 passageObject = processPassage(passage, i + 1)

#                 passageObject.header = headers[i]
#                 passageObject.questionNumbers = ",".join([str(x) for x in qnos[i]])

#                 section = computeSection(passageObject, passageObjects, section)
#                 passageObject.section = section

#                 if section >= 2:
#                     break
#                 passageObjects.append(passageObject)
#             # Save to dataframe
#             df = asPanadasDF(passageObjects, paperNumber)
#             saveDataFrame(df, f"output/sat2/SAT{paperNumber}Passages.xlsx")
#             finalDataFrame = merge2dataframes(finalDataFrame, df)
#         except Exception as e:
#             print(f"Error in paper {paperNumber}: {e}")
#             continue
#     saveDataFrame(finalDataFrame, f"output/sat2/final/SATPassages.xlsx")