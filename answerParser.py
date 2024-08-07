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


def parse_answer(doc) -> List[AnswerTmp]:
    all_answers = []
    section = 1
    current_question = 1
    answers = []
    for page in doc:
        line = []
        blocks = page.get_text("blocks")
        border = 270
        answer_page = False
        for block in blocks:
            if ("ANSWER KEY" in block[4] or "ANSWERS TO READING COMPREHENSION EXERCISES" in block[4]):
                answer_page = True
            if not answer_page:
                continue

            # print(block)
            answer_match = re.findall(r"(\d+)\.\s+([A-E])", block[4])

            # answer_match = re.findall(r'(?<!.)(\d+)\.', block[4])
            if len(answer_match) > 0:
                # print(answer_match, block[4])
                for answer in answer_match:
                    current_question = answer[0]
                    option = answer[1]
                    all_answers.append(AnswerTmp(section, current_question, option))
                    answers.append(current_question)

    print(len(all_answers))
    print(answers)

    return all_answers
