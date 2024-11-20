from gemini_utilities import *
import re
import markdown

def get_correct_option(question):
    options = question["options"]
    for option in options:
        if option["is_correct"]:
            return option["description"]

    return "no answer"

def get_all_options(question):
    options = question["options"]
    return [option["description"] for option in options]

def clean_reading_material(path):
    quiz = read_json_file(path)

    for question in quiz["questions"]:
        if "html_with_keywords" not in question:
            continue
        html_with_keywords = question["html_with_keywords"]

        html_with_keywords = html_with_keywords.replace('style=\"color:red;\"', "")
        html_with_keywords = html_with_keywords.replace('style=\"color:red\"', "")
        html_with_keywords = html_with_keywords.replace('style=\"background-color:yellow\"', "")
        html_with_keywords = html_with_keywords.replace('style=\"background-color:yellow;\"', "")
        html_with_keywords = markdown.markdown(html_with_keywords)
        
        title_regex = r"<title>.*?</title>"
        html_with_keywords = re.sub(title_regex, "", html_with_keywords)

        question["html_with_keywords"] = html_with_keywords

    remove_empty_questions(quiz)
    write_json_file(path, quiz)
    find_unanswerable_questions(path)

def remove_empty_questions(quiz):
    for question in quiz["questions"]:
        if "html_with_keywords" in question and len(question["html_with_keywords"].split()) < 100:
            del question["html_with_keywords"]

def repopulate_unanswerable_questions(question):
    if "html_with_keywords" not in question:
        return
    
    if question["is_answerable"] != False:
        return

    print(question["id"])
    print(question["description"])
    prompt = f"""
    question: {question["description"]}
    options: {get_all_options(question)}
    answer: {get_correct_option(question)}

    Modify the content below so that it contains enough information to answer the question.
    *Skip the part where the question and answer are discussed*
    mark the answer to the question in <span class="highlight"></span> tags.

    html content:
    {question["html_with_keywords"]}
    """
    response = model.generate_content(prompt)
    try:
        question["html_with_keywords"] = get_html_from_response(response.text)
    except Exception as e:
        print(e)

    # write_json_file(path, quiz)

def filter_is_answerable(question):
    if "false" in question["is_answerable"].lower():
        question["is_answerable"] = False
    else:
        question["is_answerable"] = True

def is_answerable(question):
    if "html_with_keywords" not in question or len(question["html_with_keywords"]) < 100:
        question["is_answerable"] = False
        repopulate_unanswerable_questions(question)
        return
    
    prompt = f"""
    Does the given content contain enough information to answer the following question?
    question: {question["description"]}
    answer: {get_correct_option(question)}


    content:
    {question["html_with_keywords"]}

    output: true or false
    """
    response = model.generate_content(prompt)

    try:
        question["is_answerable"] = response.text
    except:
        question["is_answerable"] = False

    filter_is_answerable(question)
    repopulate_unanswerable_questions(question)

    
def find_unanswerable_questions(quiz_path):
    quiz = read_json_file(quiz_path)
    for question in quiz["questions"]:
        is_answerable(question)

    write_json_file(quiz_path, quiz)

# find_unanswerable_questions("/Users/pranav/GitHub/pdf-parsing/gemini/Neet/5.json")
# find_unanswerable_questions("/Users/pranav/GitHub/pdf-parsing/gemini/Neet/50.json")
# find_unanswerable_questions("/Users/pranav/GitHub/pdf-parsing/gemini/Neet/51.json")
# find_unanswerable_questions("/Users/pranav/GitHub/pdf-parsing/gemini/Neet/52.json")


# clean_reading_material("/Users/pranav/GitHub/pdf-parsing/gemini/Neet/5.json")
# clean_reading_material("/Users/pranav/GitHub/pdf-parsing/gemini/Neet/50.json") 
# clean_reading_material("/Users/pranav/GitHub/pdf-parsing/gemini/Neet/51.json") 
# clean_reading_material("/Users/pranav/GitHub/pdf-parsing/gemini/Neet/52.json") 
