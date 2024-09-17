from gemini_api import *
import re
import pandas as pd
import time
from google.api_core.exceptions import ResourceExhausted


def get_prompt(qn, correct_option, topic):
    return f"""
    question: {qn}
    answer: {correct_option}

    The question belongs to the topic '{topic}' to prepare for NEET exam. Give detailed explanation why the answer is correct.

    If there are steps involved in solving, provide step by step approach. Also add the relevant formulas required to solve the question.

    Also add few learning statement for a student preparing for NEET exam related to the topic '{topic}' with respect to the question.
    """


def get_correct_option(question):
    options = question["options"]
    for option in options:
        if option["is_correct"]:
            return option["description"]

    return "no answer"


def get_detailed_solution(question, topic):
    try:

        response = model.generate_content(
            get_prompt(question["description"], get_correct_option(question), topic))

        return response.text
    except ResourceExhausted as e:
        print(e)
        return get_detailed_solution(question, topic, 10)
    except Exception as e:
        print(e)


api_key = os.environ.get("GEMINI_API_KEY")
configure_client(api_key)

model = generativeai.GenerativeModel(
    model_name="models/gemini-1.5-flash"
)


for number in range(88, 101):
    input_file_path = f"""/home/barath/Documents/Neet/{number}.json"""
    output_file_path = f"""/home/barath/Documents/NeetSolution/{number}.json"""
    solution = {}
    with open(input_file_path, 'r') as f:
        quiz = json.load(f)
        questions = quiz["questions"]
        for question in questions:
            solution[question["id"]] = get_detailed_solution(question, quiz["topic"])
            print(question["id"])
            # print(solution, "\n\n")
            time.sleep(0.1)

    with open(output_file_path, "w") as f:
        json.dump(solution, f, indent=4)
