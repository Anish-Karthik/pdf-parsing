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
    metadata: {question["keywords"]}
    content:{question["content_html"]}

    
    understand minimum **5 unique keywords** in the content based on the question,answer and the metadata.
    wrap the found keywords in the given html in a *span class="important"* - use <span class="important"></span> tags

    verify that each keyword is wrapped only once in the output html.

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