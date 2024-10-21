
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


def get_question_keywords(question, topic, neet_pdf, retry=0):
    response = model.generate_content([
        get_prompt(question["description"], get_correct_option(question), topic), neet_pdf])
    return change_response_to_list(response)


def populate_question_keywords(input_file_path, neet_pdf):
    quiz = read_json_file(input_file_path)

    questions = []
    for question in quiz["questions"]:
        if "keywords" not in question:
            questions.append(question)

    call_collection_with_threading(
        func=get_question_keywords,
        args=(quiz["topic"], neet_pdf),
        threads=10, collection=questions)

    write_json_file(input_file_path, quiz)
