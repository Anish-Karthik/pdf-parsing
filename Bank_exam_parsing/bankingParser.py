import fitz
import os
import json
from questionsParser import *


def get_invalid_questions(blocks):
    invalid = []
    directions_re = r"Direction(.*?)\((\d+).*?(\d+)\)"
    for block in blocks:
        if re.match(directions_re, block[4]):
            match_groups = re.findall(directions_re, block[4], re.IGNORECASE)
            invalid.extend([str(x) for x in range(int(match_groups[0][1]), int(match_groups[0][2]) + 1)])
    return invalid


def get_answer_map(answer_blocks):
    answer_map = {}
    answer_re = r"^[Q,S](\d+)(\.|\s)*Ans(\.|\s)*\(([a-e])\)"
    for block in answer_blocks:
      if re.search(answer_re, block[4]):
        match_groups = re.findall(answer_re, block[4])
        answer_map[match_groups[0][0]] = match_groups[0][3].upper()
    return answer_map

def filter_questions(questions_json):
    questions_json.sort(key=lambda x: int(x["qno"]))
    new_questions_json = []
    seen = set()
    for question_json in questions_json:
        if question_json["qno"] not in seen:
            new_questions_json.append(question_json)
            seen.add(question_json["qno"])

    return new_questions_json


pdfs = os.listdir("/Users/pranav/GitHub/pdf-parsing/Bank_exam_parsing/Bank Exam Materials/sbi")

print(pdfs)
for pdf in pdfs:

    if not pdf.endswith(".pdf"):
        continue
    pdf_path = "/Users/pranav/GitHub/pdf-parsing/Bank_exam_parsing/Bank Exam Materials/sbi/" + pdf
    answer_pdf_path = "/Users/pranav/GitHub/pdf-parsing/Bank_exam_parsing/Bank Exam Materials/answers/sbi/" + pdf
    if os.path.exists(pdf_path) == False or os.path.exists(answer_pdf_path) == False:
        continue

    answer_blocks = get_each_lines(fitz.open(answer_pdf_path))
    blocks = get_each_lines(fitz.open(pdf_path))
    answer_map = get_answer_map(answer_blocks)
    invalid_questions = get_invalid_questions(blocks)
    questions = get_questions_alter(blocks)

    questions_json = [question.to_json() for question in questions]

    for question_json in questions_json:
        new_options = []
        for ind, option in enumerate(question_json["options"]):
            new_options.append(option["description"])
        question_json["options"] = new_options
        question_json["reasoning"] = question_json["detailed_answer"]
        question_json["question"] = question_json["description"]
        del question_json["detailed_answer"]
        del question_json["description"]
        del question_json["references"]

        if question_json["qno"] in invalid_questions:
            question_json["valid"] = False
        else:
            question_json["valid"] = True
            
        if question_json["qno"] in answer_map:
            question_json["correct_option"] = answer_map[question_json["qno"]]
        else:
            print(pdf)
            print("change regex for ", question_json["qno"])

    questions_json = filter_questions(questions_json)

    with open(f"parsing-output/sbi/{pdf[:-4]}.json", "w") as outfile:
        json.dump(questions_json, outfile, indent=4)
