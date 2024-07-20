import os
import re

import fitz
import pandas as pd

from utils.dataframeOperation import asPanadasDF, merge2dataframes,saveDataFrame
from utils.passage import processPassage
from utils.util import write_text_to_file

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
            if is_extra(block):
                continue
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


if __name__ == '__main__':
    finalDataFrame = pd.DataFrame(columns=["Sample paper", "Section", "Question no","Passage", "Header", "Source details","Character Metadata","Word Metadata"])
    pdf_file_path = ""
    file_list = os.listdir("input/cat")

    # Iterate over each file
    for file_name in file_list[:3]:
        if file_name.endswith(".pdf"):
            pdf_file_path = os.path.join("input/cat", file_name)
            paperNumber = file_name.rstrip(".pdf")
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
                except Exception as e:
                    print("Error in section assignment:",e)
                passageObject.section = section
                passageObjects.append(passageObject)
            
            df = asPanadasDF(passageObjects, paperNumber)
            saveDataFrame(df, f"output/cat/{paperNumber}Passages.xlsx")
            finalDataFrame = merge2dataframes(finalDataFrame, df)
        except Exception as e:
            print(f"Error in paper {paperNumber}: {e}")
            continue
    saveDataFrame(finalDataFrame, f"output/cat/CATPassages.xlsx")