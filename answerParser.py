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
    
    def to_json(self) -> Dict:
        return {
            "section": self.section,
            "question_number": self.question_number,
            "answer": self.answer,
            "detailed_solution": self.detailed_solution
        }


def parse_answer(blocks) -> List[AnswerTmp]:
    all_answers = []
    section = 0
    current_question = 1
    answer_started = False
    option_started = False
    option = ""
    for block in blocks:
        if re.search(r"^Practice Test", block[4]):
            option_started = False
            continue
        if "ANSWERS EXPLAINED" in block[4]:
            answer_started = True
            option_started = False
            print("Answer started")
            continue
        if not answer_started:
            continue

        # print(block)
        # answer_match = re.findall(r"(?<!.)(\d+)\..*\(([A-D])\)", block[4])
        qno_match = re.findall(r"(?<!.)(\d+)\. $", block[4])
        if len(qno_match) > 0 and current_question == "2" and qno_match[0] == "15":
            print("debug",block,qno_match)

        elif len(qno_match) > 0:
            # print(block,qno_match)
            current_question = qno_match[0]
            if current_question == "1":
                section += 1
            if option_started and option != "":
                # split the option and detailed solution
                # option, detailed_solution = option.split(r"\(([A-D])\)", 1)
                all_answers.append(AnswerTmp(section, current_question, option))
                option = ""
            option_started = True
            continue
        if option_started:
            option += block[4]

        # if len(answer_match) > 0:
        #     current_question = answer_match[0][0]
        #     option = answer_match[0][1]
        #     all_answers.append(AnswerTmp(section, current_question, option))
    return all_answers
