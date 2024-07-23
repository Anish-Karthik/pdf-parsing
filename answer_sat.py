from PIL import Image
import pytesseract
import pandas as pd
import pdf2image
import re
import os
class SolutionParsing:
    sectionNo = 0 
    sample_paper_no = "-1"
    passage_df = pd.DataFrame(columns=["Sample paper","Section","Question No", "Answer", "Detailed solution"])

    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
    @staticmethod
    def replace_unwanted_text(text):
        text = re.sub(r'© \d{4}[^\n]*', '', text, flags=re.MULTILINE)
        text  = re.sub(r'ANSWER EXPLANATIONS \| SAT Practice Test \#\d{1,}', '', text)
        text  = re.sub(r'PART \d{1,} \| Eight Official Practice Tests with Answer Explanations  \d*', '', text)
        # print(text)
        return text
    @classmethod
    def extract_text_with_ocr(cls, pdf_path):
        try:
            text = ""
            pages = pdf2image.convert_from_path(pdf_path)
            for page_number, page in enumerate(pages):
                text += pytesseract.image_to_string(page)
            cls.sample_paper_no = cls.extractSamplePaperNumber(text)
            print("Sample Paper Number : " + str(cls.sample_paper_no) + str(type(cls.sample_paper_no)))
            cls.extractQuestions(text)
            cls.sectionNo = 0
            cls.sample_paper_no = "-1"
        except Exception as e:
            print(f"Error: {e}")
    @classmethod
    def extractSamplePaperNumber(cls, text):
        # print(text)
        if cls.sample_paper_no != "-1":
            return cls.sample_paper_no
        paper_no_pattern = r'SAT Practice Test \#(\d{1,})'
        paper_no = re.findall(paper_no_pattern,text)
        return "-1" if len(paper_no) == 0 else paper_no[0]
    @classmethod
    def extractQuestions(cls, text):
        # Regex pattern to match each question separately
        pattern = r"QUESTION \d+[\s\S]*?(?=QUESTION \d+|$)"
        questions = re.findall(pattern, text)
        rows_to_add = []
        for question in questions:
            questionNoPattern = r"QUESTION (\d{1,})"
            questionNo = int(re.findall(questionNoPattern, question)[0])
            correctOptionPattern = r"Choice(?:s)? ([A-D])";
            correctOption = re.findall(correctOptionPattern,question)
            correctOption = '' if len(correctOption) == 0 else correctOption[0]
            if questionNo == 1:
                cls.sectionNo += 1  # Increment class variable sectionNo for each new section
            formatted_question = question.strip().replace('QUESTION '+str(questionNo),'').replace('\n',' ');
            formatted_question = cls.replace_unwanted_text(formatted_question)
            formatted_question = re.sub(correctOptionPattern, r'\nChoice \1', formatted_question)
            row = {
                "Sample paper": cls.sample_paper_no,
                "Section": cls.sectionNo,
                "Question No": questionNo,
                "Answer": correctOption,
                "Detailed solution": formatted_question
            }
            rows_to_add.append(row)
        cls.passage_df = pd.concat([cls.passage_df, pd.DataFrame(rows_to_add)], ignore_index=True)
    def export_to_excel(filename):
        try:
            SolutionParsing.passage_df.to_excel(filename, index=False)
            print(f"Data exported to {filename} successfully.")
        except Exception as e:
            print(f"Error exporting to Excel: {e}")
# Example usage:
if __name__ == "__main__":
    current_path = os.getcwd()
    folders = os.listdir(current_path)
    pdf_files = []
    for i in folders:
        if i.endswith(".pdf"):
            pdf_files.append(i)
    pdf_files.sort()
    for i in pdf_files:
        print(i)
        SolutionParsing.extract_text_with_ocr(i)
    SolutionParsing.export_to_excel("SAT_Solution.xlsx")