from gemini_utilities import *
import threading


def get_correct_option(question):
    options = question["options"]
    for option in options:
        if option["is_correct"]:
            return option["description"]

    return "no answer"


def get_highlighted_html(question):

    prompt = f"""
    question: {question["description"]}
    answer: {get_correct_option(question)}
    keywords: {question["keywords"]}

    wrap *unique* important data and keywords based on the question,answer in the given html in a *span class="important"*

    rules:
    - use <span class="important"></span> tags
    - if one occurance of keyword is wrapped in <span class="important"> tag, do not wrap other occurances of keyword in <span class="important"> tag

    html:

    {question["content_html"]}
    """
    question["html_with_keywords"] = model.generate_content(
        prompt
    ).text

    question["html_with_keywords"] = question["html_with_keywords"].replace("```html\n", "")
    question["html_with_keywords"] = question["html_with_keywords"].replace("\n```", "")
    question["html_with_keywords"] = question["html_with_keywords"].replace("\n", "")
    question["html_with_keywords"] = question["html_with_keywords"].replace("\\\"", r"\"")


def highlight_keywords(path):

    quiz = read_json_file(path)

    call_collection_with_threading(
        func=get_highlighted_html,
        threads=10,
        collection=quiz["questions"]
    )

    write_json_file(path, quiz)
