
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
    question["keywords"] = change_response_to_list(response.text)


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

def get_tamil_prompt(qn, correct_option, topic):
    return f"""
    question: {qn}
    answer: {correct_option}

    The question belongs to the topic 'Tamil - {topic}'

    Give top 5 keywords for the question to prepare on the topic to understand the question better.

    **Note: The question is in Tamil language**
    **Output should be in Tamil language**

    output: **Return the keywords as an array of strings**
    """

def get_question_keywords_tamil(question, topic, tamil_pdf):
    response = model.generate_content([
        get_tamil_prompt(question["description"], get_correct_option(question), topic), tamil_pdf])
    question["keywords"] = change_response_to_list(response)

def populate_question_keywords_tamil(input_file_path, tamil_pdf_path):
    quiz = read_json_file(input_file_path)

    questions = []
    for question in quiz["questions"]:
        if "keywords" not in question:
            questions.append(question)

    if len(questions) == 0:
        return
    
    if len(questions) > 0:
        tamil_pdf = upload_file_to_gemini(tamil_pdf_path)

    call_collection_with_threading(
        func=get_question_keywords_tamil,
        args=(quiz["topic"], tamil_pdf),
        threads=10, collection=questions)

    write_json_file(input_file_path, quiz)

