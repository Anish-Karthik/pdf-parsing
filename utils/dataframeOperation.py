from typing import List
import pandas as pd
from classes.passage import Passage

def asPanadasDF(passages: List[Passage], paperNumber) -> pd.DataFrame:
    df = pd.DataFrame(columns=["Sample paper", "Section", "Question no","Passage", "Header", "Source details","Character Metadata","Word Metadata"])
    for i, passage in enumerate(passages):
        df = pd.concat([df, pd.DataFrame({
            "Sample paper": [paperNumber],
            "Section": [passage.section],
            "Question no": [passage.questionNumbers],
            "Passage": [passage.text],
            "Header": [passage.header],
            "Source details": [passage.source_details],
            "Character Metadata": [passage.characterMetadata.jsonize()],
            "Word Metadata": [passage.wordMetadata.jsonize()]
        })], ignore_index=True)
    return df

def saveDataFrame(df: pd.DataFrame, filename: str) -> None:
    writer = pd.ExcelWriter(filename, engine='xlsxwriter')
    df.to_excel(writer, index=False)
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']
    format_wrap = workbook.add_format({'text_wrap': True, 'valign': 'top'})
    for i in range(3):
        worksheet.set_column(i, i, 13, format_wrap)
    for i in range(3, len(df.columns)):
        worksheet.set_column(i, i, 60, format_wrap)
    writer.close()

def saveAsExcel(passages: List[Passage], filename: str, paperNumber) -> None:
    df = asPanadasDF(passages, paperNumber)
    print(df)
    saveDataFrame(df, filename)
    

def merge2dataframes(df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
    return pd.concat([df1, df2], ignore_index=True)

def mergeNdataframes(dfs: List[pd.DataFrame]) -> pd.DataFrame:
    return pd.concat(dfs, ignore_index=True)