from gemini_utilities import *
import threading

def get_all_options(question):
    options = question["options"]
    return [option["description"] for option in options]

def get_correct_option(question):
    options = question["options"]
    for option in options:
        if option["is_correct"]:
            return option["description"]

    return "no answer"


def get_highlighted_html(question):
    prompt = f"""
    im a student revising the following content, mark the technical terms as important for me to revise.
    highlight the given content using <span class="important"></span> tags.
    dont highlight anything in h tags

    content:{question["content_html"]}
    """
    question["html_with_keywords"] = model.generate_content(
        prompt
    ).text

    question["html_with_keywords"] = question["html_with_keywords"].replace("```html\n", "")
    endIndex = question["html_with_keywords"].find("\n```")
    question["html_with_keywords"] = question["html_with_keywords"][:endIndex]
    question["html_with_keywords"] = question["html_with_keywords"].replace("\n", "")
    question["html_with_keywords"] = question["html_with_keywords"].replace("\\\"", r"\"")

    with open(f"/Users/pranav/Desktop/h-{question['id']}.html", "w") as f:
        f.write(question["html_with_keywords"])

def highlight_background(question):
    prompt = f"""
    question:{question["description"]}
    options:{get_all_options(question)}
    correct_option:{get_correct_option(question)}

    mark the relevant portion required to answer the question in the content using <span class="highlight"></span> tags.

    content:{question["html_with_keywords"]}
    """
    question["html_with_keywords"] = model.generate_content(
        prompt
    ).text

    question["html_with_keywords"] = question["html_with_keywords"].replace("```html\n", "")
    endIndex = question["html_with_keywords"].find("\n```")
    question["html_with_keywords"] = question["html_with_keywords"][:endIndex]
    question["html_with_keywords"] = question["html_with_keywords"].replace("\n", "")
    question["html_with_keywords"] = question["html_with_keywords"].replace("\\\"", r"\"")

    with open(f"/Users/pranav/Desktop/h-{question['id']}.html", "w") as f:
        f.write(question["html_with_keywords"])

def highlight_background_all(path):
    quiz = read_json_file(path)
    call_collection_with_threading(
        func=highlight_background,
        threads=10,
        collection=quiz["questions"]
    )
    write_json_file(path, quiz)

def highlight_keywords(path):

    quiz = read_json_file(path)

    call_collection_with_threading(
        func=get_highlighted_html,
        threads=10,
        collection=quiz["questions"]
    )

    write_json_file(path, quiz)
