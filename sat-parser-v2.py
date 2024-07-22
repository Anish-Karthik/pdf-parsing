import os
import re

import fitz
import pandas as pd
from utils.dataframeOperation import asPanadasDF, merge2dataframes,saveDataFrame
from utils.passage import processPassage
from utils.util import write_text_to_file


def isStartOfPassage(block):
    return bool(re.match(r'Questions \d*-\d*', block[4]))

def isEndOfPassage(block, qno = None):
    if qno:
        return re.search(r"^"+str(qno), block[4])
    return block[0] in [338.7315979003906, 318.2538146972656, 39.872100830078125, 42.38639831542969]

def parseQuestionNumber(block) -> list:
    tmp = [int(x) for x in re.findall(r"\d+", block[4])]
    if tmp is None:
        return []
    st, end = tmp
    return list(range(st, end+1))

def is_extra(block) -> bool:
    # isNum = bool(re.match(r"\d+\n",block[4]))
    # if not alphanumeric
    return (
        re.search(r"Line\n5?",block[4]) or
        re.search(r"Unauthorized copying", block[4]) or
        re.search(r"CO NTI N U E", block[4]) or
        re.search(r"STOP", block[4]) or
        not re.search(r'[a-zA-Z]', block[4])
    )


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
            if isPassageStarted:
                if isEndOfPassage(block, qnos[-1][0]):
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
                qnos.append(parseQuestionNumber(block))
                isPassageStarted = True
                continue
    print(passages)
    write_text_to_file("\n\n\n\n".join(passages), "debug/SAT1tempPassages.txt")
    print(qnos)
    return (headers,passages,qnos)

if __name__ == '__main__':
    finalDataFrame = pd.DataFrame(columns=["Sample paper", "Section", "Question no","Passage", "Header", "Source details","Character Metadata","Word Metadata"])
    pdf_file_path = ""
    file_list = os.listdir("input/sat")

    # Iterate over each file
    for paperNumber, file_name in enumerate(file_list[3:4], start=4):
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
    saveDataFrame(finalDataFrame, f"output/sat2/SATPassages.xlsx")