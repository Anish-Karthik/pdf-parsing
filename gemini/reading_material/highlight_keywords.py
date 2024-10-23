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

    understand the content, question and metadata, return the unique    keywords/ important words
    """
    response = model.generate_content(prompt)
    print(response.text)

    prompt = f"""
    keywords: {response.text}
    content:{question["content_html"]}

    mark the first occurrence of each keyword exactly once in the given html in a using <span class="important"></span> tags
    each keyword should be marked important only once

    verify that each keyword is wrapped only once in the output html.

    """
    question["html_with_keywords"] = model.generate_content(
        prompt
    ).text

    question["html_with_keywords"] = question["html_with_keywords"].replace("```html\n", "")
    endIndex = question["html_with_keywords"].find("\n```")
    question["html_with_keywords"] = question["html_with_keywords"][:endIndex]
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
