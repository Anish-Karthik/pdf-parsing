
import json
import os
import threading
import google.generativeai as generativeai
from google.api_core.exceptions import ResourceExhausted
import pandas as pd
from gemini_utilities import *


def get_prompt(qn, correct_option, topic):
    return f"""
    question: {qn}
    answer: {correct_option}

    The question belongs to the topic 'Biology - {topic}' from NCERT book.

    Give top 5 keywords for the question to prepare on the topic to understand the question better.

    output: **Return the keywords as an array of strings**
    """


def get_correct_option(question):
    options = question["options"]
    for option in options:
        if option["is_correct"]:
            return option["description"]

    return "no answer"


def get_json_response(response):
    text = response.text
    text = text.replace("```json", "")
    text = text.replace("```", "")
    return json.loads(text)


def get_question_keywords(question, topic, neet_pdf, retry=0):
    try:
        response = model.generate_content([
            get_prompt(question["description"], get_correct_option(question), topic), neet_pdf])

        print(question["id"])
        print(question["description"])
        print(get_correct_option(question))

        keywords = response.text
        keywords = keywords.replace("```json", "")
        keywords = keywords.replace("```", "")
        try:
            get_json_response(response)

            question["keywords"] = get_json_response(response)
        except Exception as e:
            if retry == 3:
                return
            return get_question_keywords(question, topic, neet_pdf, retry + 1)
    except ResourceExhausted as e:
        print(e)
        return get_question_keywords(question, topic, neet_pdf)
    except Exception as e:
        print(e)


api_key = os.environ.get("GEMINI_API_KEY")
generativeai.configure(api_key=api_key)

model = generativeai.GenerativeModel(
    model_name="models/gemini-1.5-flash"
)


def split_into_batches(array, batch_size=5):
    return [array[i:i + batch_size] for i in range(0, len(array), batch_size)]


def populate_question_keywords(input_file_path, neet_pdf):
    with open(input_file_path, 'r') as f:
        quiz = json.load(f)

        questions = []
        for question in quiz["questions"]:
            if "keywords" not in question:
                questions.append(question)

        question_batches = split_into_batches(questions, 5)
        for question_batch in question_batches:
            threads = []
            for question in question_batch:
                thread = threading.Thread(target=get_question_keywords, args=(question, quiz["topic"], neet_pdf))
                threads.append(thread)
                thread.start()
            for thread in threads:
                thread.join()

    with open(input_file_path, "w") as f:
        json.dump(quiz, f, indent=4)

