import os
import re

import fitz
import pandas as pd
from utils.dataframeOperation import asPanadasDF, merge2dataframes,saveDataFrame
from utils.passage import processPassage
from utils.util import write_text_to_file


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

def getReferences(passage: str, startline: int, endLine = None):
    print("REFERENCES number", startline, endLine)
    lines = passage.split("\n")
    startline -= 1
    if endLine:
        endLine -= 1
    startWord = len(" ".join(lines[:startline]).split())
    if not endLine:
        endLine = startline
    if endLine == len(lines):
        endWord = len(" ".join(lines).split())
    endWord = len(" ".join(lines[:endLine + 1]).split())
    print(re.sub(r"\n", " ", passage).split()[startWord:endWord])
    print("References:", startWord, endWord)
    return (startWord, endWord)

def cleanPassage(passage: list) -> str:
    text = "".join([b[4] for b in passage]).strip()
    text = re.sub(r"\n+", "\n", text)
    tmp =  text.split("\t", 1)
    text = tmp[1] if len(tmp) > 1 else text
    return text

def extract_passages_from_pdf(pdf_file: str = "input/sat/SAT Practice Test 1.pdf"):
    doc = fitz.open(pdf_file)
    passages = []
    isPassageStarted = False
    passage = []
    headers = []
    qnos = []
    
    for page in doc:
        blocks = page.get_text("blocks") 
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
    return (headers,passages,qnos)

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

extract_passages_from_pdf()



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