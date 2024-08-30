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
        if "ANSWERS EXPLAINED" in block[4]:
            answer_started = True
            continue
        if not answer_started:
            continue

        # print(block)
        # answer_match = re.findall(r"(?<!.)(\d+)\..*\(([A-D])\)", block[4])
        qno_match = re.findall(r"(?<!.)(\d+)\.\s*(\([A-D]\))", block[4])
        if len(qno_match) > 0 and current_question == "2" and qno_match[0] == "15":
            print("debug",block,qno_match)

        if len(qno_match) > 0 and qno_match[0][0] == "1":
            section += 1
        
        if len(qno_match) > 0:
            answer = block[4]
            correct_option = re.findall(r"\d+.\s\([A-D]\)",answer)[0]
            correct_option = re.search(r"[A-D]", correct_option).group(0)
            
            all_answers.append(AnswerTmp(section, qno_match[0][0], correct_option))
        

        # elif len(qno_match) > 0:
        #     # print(block,qno_match)
        #     current_question = qno_match[0]
        #     if current_question == "1":
        #         section += 1
        #     if option_started and option != "":
        #         # split the option and detailed solution
        #         # option, detailed_solution = option.split(r"\(([A-D])\)", 1)
        #         all_answers.append(AnswerTmp(section, current_question, option))
        #         option = ""
        #     option_started = True
        #     continue
        # if option_started:
        #     option += block[4]

        # if len(answer_match) > 0:
        #     current_question = answer_match[0][0]
        #     option = answer_match[0][1]
        #     all_answers.append(AnswerTmp(section, current_question, option))
    # for answer in all_answers:
    #     print(answer)
    return all_answers
