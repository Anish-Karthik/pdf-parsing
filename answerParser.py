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
    answer_started = False
    for block in blocks:
        if "ANSWERS EXPLAINED" in block[4]:
            answer_started = True
            continue
        if not answer_started:
            continue

        # print(block)
        answer_match = re.findall(r"(?<!.)(\d+)\.\s+\(([A-D])\)", block[4])

        if len(answer_match) > 0:
            current_question = answer_match[0][0]
            option = answer_match[0][1]
            all_answers.append(AnswerTmp(section, current_question, option))
    return all_answers
