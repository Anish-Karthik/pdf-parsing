import pdfplumber
import pandas as pd
import re
import os
from typing import List, Tuple, Any

def mapNumberToLetter(num):
    return chr(int(num.strip())+64)

def get_all_answers(pdf_path) -> List[Tuple[str, str]]:
    pdf = pdfplumber.open(pdf_path)
    table_rows = []
    answer_column = -1
    question_column = -1
    for page in pdf.pages:
        text = page.extract_text()
        if not re.search(r'Answer [kK]eys:*', text):
            continue
        table_data = page.extract_table()[0:]
        for row in table_data:
            if question_column == -1:
                answer_column = row.index("Answer") if "Answer" in row else row.index("VARC") if "VARC" in row else -1
                question_column = next((row.index(s) for s in row if re.search(r'Q\.\s*No\.*', "" if not s else s)), -1)
                if question_column == -1:
                    question_column = row.index("Question No.") if "Question No." in row else -1
                continue
            table_rows.append([row[question_column],row[answer_column]])
    print(table_rows[:16])
    return [ (qno,mapNumberToLetter(x)) for (qno, x) in table_rows[:16]]