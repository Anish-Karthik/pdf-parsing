from utils.util import write_text_to_file
from parser import extract_text_from_pdf
from utils.passage import PassageUtils, processPassage
from utils.dataframeOperation import asPanadasDF,merge2dataframes,saveDataFrame
import pandas as pd
from utils.underline import Underline

if __name__ == '__main__':
    paperNumber = 1
    finalDataFrame = pd.DataFrame(columns=["Sample paper", "Section", "Question no","Passage", "Header", "Source details","Character Metadata","Word Metadata"])
    for paperNumber in range(1, 2):
        try:
            pdf_file_path = f"input/sat{paperNumber}QP_removed.pdf"
            pdf_text = extract_text_from_pdf(pdf_file_path)
            all_text = "".join(pdf_text)
            passages = PassageUtils.pre_process_passages(all_text)
            underlineObject = Underline()
            underlineObject.read_all_underline_sentences(pdf_file_path)

            # print(underlineObject.all_underline_sentences)
            passageObjects = []
            for i, passage in enumerate(passages):
                passageObjects.append(processPassage(passage, i + 1, underlineObject))

            write_text_to_file("****************************************\n\n\n".join(passages), "debug/SAT1tempPassages.txt")
            write_text_to_file("".join(pdf_text), "debug/SAT1temp.txt")

            df = asPanadasDF(passageObjects, paperNumber)
            saveDataFrame(df, f"output/SAT{paperNumber}Passages.xlsx")
            finalDataFrame = merge2dataframes(finalDataFrame, df)
        except Exception as e:
            print(f"Error in paper {paperNumber}: {e}")
            continue
    # saveDataFrame(finalDataFrame, f"output/SAT1-8Passages.xlsx")