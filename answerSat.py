from PIL import Image
import pytesseract
import pandas as pd
import pdf2image
import re
import os
from typing import *

class AnswerTmp:
    def __init__(self, section: int, question_number: int, answer: str, detailed_solution: Optional[str] = None):
        self.section = section 
        self.question_number = question_number
        self.answer = answer
        self.detailed_solution = detailed_solution
    
    def __str__(self) -> str:
        return f"Section: {self.section}, Question Number: {self.question_number}, Answer: {self.answer}, Detailed Solution: {self.detailed_solution}"

class SolutionParsing:
    sectionNo = 0 
    sample_paper_no = "-1"

    @staticmethod
    def replace_unwanted_text(text):
        text = re.sub(r'© \d{4}[^\n]*', '', text, flags=re.MULTILINE)
        text  = re.sub(r'ANSWER EXPLANATIONS \| SAT Practice Test \#\d{1,}', '', text)
        text  = re.sub(r'PART \d{1,} \| Eight Official Practice Tests with Answer Explanations  \d*', '', text)
        # print(text)
        return text
    @classmethod
    def extract_text_with_ocr(cls, pdf_path = "C:/Users/anish/Documents/_intern/testline-intern/pdf-parsing/input/sat-answers/SAT Practice Test 1.pdf") -> List[AnswerTmp]:
            text = ""
            pages = pdf2image.convert_from_path(pdf_path)
            for page_number, page in enumerate(pages):
                text += pytesseract.image_to_string(page)
            cls.sample_paper_no = cls.extractSamplePaperNumber(text)
            print("Sample Paper Number : " + str(cls.sample_paper_no) + str(type(cls.sample_paper_no)))
            cls.sectionNo = 0
            cls.sample_paper_no = "-1"
            return cls.extractAnswers(text)
    @classmethod
    def extractSamplePaperNumber(cls, text):
        # print(text)
        if cls.sample_paper_no != "-1":
            return cls.sample_paper_no
        paper_no_pattern = r'SAT Practice Test \#(\d{1,})'
        paper_no = re.findall(paper_no_pattern,text)
        return "-1" if len(paper_no) == 0 else paper_no[0]
    @classmethod
    def extractAnswers(cls, text) -> List[AnswerTmp]:
        # Regex pattern to match each question separately
        pattern = r"QUESTION \d+[\s\S]*?(?=QUESTION \d+|$)"
        questions = re.findall(pattern, text)
        answerObjects = []
        for question in questions:
            questionNoPattern = r"QUESTION (\d{1,})"
            questionNo = int(re.findall(questionNoPattern, question)[0])
            correctOptionPattern = r"Choice(?:s)? ([A-D])";
            correctOption = re.findall(correctOptionPattern,question)
            correctOption = '' if len(correctOption) == 0 else correctOption[0]
            if questionNo == 1:
                cls.sectionNo += 1  # Increment class variable sectionNo for each new section

            detailed_solution = question.strip().replace('QUESTION '+str(questionNo),'').replace('\n',' ');
            detailed_solution = cls.replace_unwanted_text(detailed_solution)
            detailed_solution = re.sub(correctOptionPattern, r'\nChoice \1', detailed_solution)

            answerObj = AnswerTmp(cls.sectionNo, questionNo, correctOption, detailed_solution)
            print(answerObj)
            answerObjects.append(answerObj)
        return answerObjects