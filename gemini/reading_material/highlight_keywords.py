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
    question: {question["description"]}
    options: {"\n".join(get_all_options(question))}
    answer: {get_correct_option(question)}
    keywords: {question["keywords"]}
    
    we want to create an interactive reading material based on the below content, mark certain keywords as important for the reader to be engaged in the content,
    in the given html by using <span class="important"></span> tags

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


def highlight_keywords(path):

    quiz = read_json_file(path)

    call_collection_with_threading(
        func=get_highlighted_html,
        threads=10,
        collection=quiz["questions"]
    )

    write_json_file(path, quiz)
