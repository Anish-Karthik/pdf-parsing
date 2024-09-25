from gemini_api import *
import re
import pandas as pd
import time
from google.api_core.exceptions import ResourceExhausted
import threading


def get_prompt(qn, correct_option, topic):
    return f"""
    question: {qn}
    answer: {correct_option}

    The question belongs to the topic 'Tamil - {topic}' to prepare for TNPSC exam. Give detailed explanation why the answer is correct.

    If there are additional context available on the question description or the topic, provide them as well.
    The content should be useful for a student to learn and apply the same content for answering similar questions.

    The solution should be in Tamil and simple to understand.
    """


def get_correct_option(question):
    options = question["options"]
    for option in options:
        if option["is_correct"]:
            return option["description"]

    return "no answer"


def get_detailed_solution(question, topic, solution):
    try:
        response = model.generate_content(
            get_prompt(question["description"], get_correct_option(question), topic))

        print(question["id"])

        solution[question["id"]] = response.text
    except ResourceExhausted as e:
        print(e)
        return get_detailed_solution(question, topic, 10)
    except Exception as e:
        print(e)


api_key = os.environ.get("GEMINI_API_KEY")
configure_client(api_key)

model = generativeai.GenerativeModel(
    model_name="models/gemini-1.0-pro"
)


def split_into_batches(array, batch_size=5):
    return [array[i:i + batch_size] for i in range(0, len(array), batch_size)]


directory_path = "/home/barath/Documents/tamil/"
output_file_path = f"""/home/barath/Documents/tamilSolution/solutions.json"""
solution = {}
with open(output_file_path, 'r') as f:
    solution = json.load(f)
for root, dirs, files in os.walk(directory_path):
    for file in files:
        input_file_path = os.path.join(root, file)
        file_name = os.path.basename(input_file_path)

        with open(input_file_path, 'r') as f:
            quiz = json.load(f)
            question_batches = split_into_batches(quiz["questions"], 30)
            for question_batch in question_batches:
                threads = []
                for question in question_batch:
                    if question["detailed_solution"] is not None and len(question["detailed_solution"]) > 0:
                        continue
                    if question["id"] in solution:
                        continue
                    thread = threading.Thread(target=get_detailed_solution, args=(question, quiz["topic"], solution))
                    threads.append(thread)
                    thread.start()
                for thread in threads:
                    thread.join()

        with open(output_file_path, "w") as f:
            json.dump(solution, f, indent=4)
