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
        return re.search(r"^"+str(qno)+"", block[4])
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


def extract_passages_from_pdf(pdf_file: str = "input/sat/SAT Practice Test 4.pdf"):
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
            if isPassageStarted:
                tmp = None
                try: tmp = qnos[-1][0] 
                except IndexError: pass
                if isEndOfPassage(block, tmp):
                    isPassageStarted = False
                    passages.append("".join(passage))
                    passage = []
                    continue
                if is_extra(block):
                    continue
                passage.append(block[4])
                continue
            if isStartOfPassage(block):
                headers.append(block[4])
                qnos.append(parseQuestionNumber(fixBugForPassage4(block[4])))
                isPassageStarted = True
                continue
    # print(passages)
    write_text_to_file("\n\n\n\n".join(passages), "debug/SAT1tempPassages.txt")
    # print(qnos)
    # print(headers)
    return (headers,passages,qnos)
# extract_passages_from_pdf()
if __name__ == '__main__':
    finalDataFrame = pd.DataFrame(columns=["Sample paper", "Section", "Question no","Passage", "Header", "Source details","Character Metadata","Word Metadata"])
    pdf_file_path = ""
    file_list = os.listdir("input/sat")

    # Iterate over each file
    for paperNumber, file_name in enumerate(file_list, start=1):
        if file_name.endswith(".pdf"):
            pdf_file_path = os.path.join("input/sat", file_name)
            # paperNumber = file_name.rstrip(".pdf")
        try:
            [headers,passages,qnos] = extract_passages_from_pdf(pdf_file_path)
            passageObjects = []
            section = 1
            for i, passage in enumerate(passages):
                # section assignment
                passageObject = processPassage(passage, i + 1)
                passageObject.header = headers[i]
                passageObject.questionNumbers = ",".join([str(x) for x in qnos[i]])
                try:
                    if len(passageObjects) > 1:
                        prevQuestionNumbers = passageObjects[-1].questionNumbers.split(",")
                        currQuestionNumbers = passageObject.questionNumbers.split(",")
                        if int(prevQuestionNumbers[-1]) > int(currQuestionNumbers[0]) and int(prevQuestionNumbers[-1]) > 0 and int(currQuestionNumbers[0]) > 0:
                            section += 1
                    if section >= 2:
                        break
                except Exception as e:
                    print("Error in section assignment:",e)
                passageObject.section = section
                passageObjects.append(passageObject)
            
            df = asPanadasDF(passageObjects, paperNumber)
            saveDataFrame(df, f"output/sat2/SAT{paperNumber}Passages.xlsx")
            finalDataFrame = merge2dataframes(finalDataFrame, df)
        except Exception as e:
            print(f"Error in paper {paperNumber}: {e}")
            continue
    saveDataFrame(finalDataFrame, f"output/sat2/final/SATPassages.xlsx")