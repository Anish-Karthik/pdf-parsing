import re
from typing import *

class AnswerTmp:
    def __init__(self, section: int, question_number: int, answer: str, detailed_solution: Optional[str] = None):
        self.section = section 
        self.question_number = question_number
        self.answer = answer
        self.detailed_solution = detailed_solution
    
    def __str__(self) -> str:
        return f"Section: {self.section}, Question Number: {self.question_number}, Answer: {self.answer}, Detailed Solution: {self.detailed_solution}"
    
def parse_answer(blocks) -> List[AnswerTmp]:
    all_answers = []
    section = 1
    current_question = 1
    for block in blocks:
        # print(block[4])
        option_match = re.findall(r"Choice\s+(.)\sis\s(correct|the best)", block[4])
        question_match = re.findall(r"QUESTION\s+(\d+)", block[4])
        
        if len(question_match) > 0 and question_match[0] == "1" and current_question != 1:
            section += 1
            current_question = 1
            if section > 2:
                break

        if (len(option_match) > 0):
            print(current_question, option_match[0][0], section)
            all_answers.append(AnswerTmp(section, current_question, option_match[0][0]))
            current_question += 1
    return all_answers
