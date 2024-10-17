from gemini_api import *
import re
import pandas as pd
import time
from google.api_core.exceptions import ResourceExhausted
import threading


def get_prompt(qn, correct_option):
    return f"""
    question: {qn}
    answer: {correct_option}

    The question belongs to TNPSC exam preparation in **maths topic**. Give detailed explanation why the answer is correct.

    **Provide step by step answer for solving the problem.** Provide any formula required clearly. An average student should understand the solution without any further help.

    The solution should be in Tamil and simple to understand.

    Make sure that the solution provided is clear and readable without any error.
    """


def get_correct_option(question):
    options = question["options"]
    for option in options:
        if option["is_correct"]:
            return option["description"]

    return "no answer"


def get_detailed_solution(question, solution):
    try:
        response = model.generate_content(
            get_prompt(question["description"], get_correct_option(question)))

        print(question["id"])

        solution[question["id"]] = response.text
    except ResourceExhausted as e:
        print(e)
        return get_detailed_solution(question, 10)
    except Exception as e:
        print(e)


api_key = os.environ.get("GEMINI_API_KEY")
configure_client(api_key)

model = generativeai.GenerativeModel(
    model_name="models/gemini-1.5-pro"
)


def split_into_batches(array, batch_size=5):
    return [array[i:i + batch_size] for i in range(0, len(array), batch_size)]


directory_path = "/home/barath/Documents/tamil/"
output_file_path = f"""/home/barath/Documents/tamilSolution/56.json"""
solution = {}
input_file_path = directory_path + "56-கணிதம் - அளவு திறன்.json"

with open(input_file_path, 'r') as f:
    quiz = json.load(f)
    # print(question_batches)
    threads = []
    for question in quiz["questions"]:
        # print(question)
        thread = threading.Thread(target=get_detailed_solution, args=(question, solution))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()

with open(output_file_path, "w") as f:
    json.dump(solution, f, indent=4)


print(len(solution))
