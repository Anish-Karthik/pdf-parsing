import os
import pandas as pd

from parser import extract_text_from_pdf
from utils.dataframeOperation import asPanadasDF, merge2dataframes, saveDataFrame
from utils.passage import PassageUtils, processPassage
from utils.underline import Underline
from utils.util import write_text_to_file

if __name__ == '__main__':
    paperNumber = 1
    finalDataFrame = pd.DataFrame(columns=["Sample paper", "Section", "Question no","Passage", "Header", "Source details","Character Metadata","Word Metadata"])
    file_list = os.listdir("input/sat")

    # Iterate over each file
    for paperNumber, file_name in enumerate(file_list, start=1):
        if file_name.endswith(".pdf"):
            pdf_file_path = os.path.join("input/sat", file_name)
            # paperNumber = file_name.rstrip(".pdf")
        try:
            pdf_text = extract_text_from_pdf(pdf_file_path)
            all_text = "".join(pdf_text)
            passages = PassageUtils.pre_process_passages(all_text)
            underlineObject = Underline()
            underlineObject.read_all_underline_sentences(pdf_file_path)

            # print(underlineObject.all_underline_sentences)
            passageObjects = []
            section = 1
            for i, passage in enumerate(passages):
                # section assignment
                passageObject = processPassage(passage, i + 1, underlineObject)
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

            write_text_to_file("****************************************\n\n\n".join(passages), "debug/SAT1tempPassages.txt")
            write_text_to_file("".join(pdf_text), "debug/SAT1temp.txt")

            df = asPanadasDF(passageObjects, paperNumber)
            saveDataFrame(df, f"output/sat/SAT{paperNumber}Passages.xlsx")
            finalDataFrame = merge2dataframes(finalDataFrame, df)
        except Exception as e:
            print(f"Error in paper {paperNumber}: {e}")
            continue
    saveDataFrame(finalDataFrame, f"output/sat/SATPassages.xlsx")