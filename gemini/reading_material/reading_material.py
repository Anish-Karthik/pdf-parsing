import json
from clean_reading_material import * 
from gemini_utilities import *
from question_keyowrd import *
from content_keyword import *
from highlight_keywords import *
from parse_pdf import *
import markdown
import threading


quiz_id_to_pdf_map = {
    # "41": "kebo105",
    # "42": "kebo106",
    # "43": "kebo107",
    # "44": "kebo108",
    # "45": "kebo109",
    # "46": "kebo110",
    # "47": "kebo111",
    # "48": "kebo112",
    # "49": "kebo113",
    # "50": "kebo114",
    # "51": "kebo115",
    # "52": "kebo116",
    # "53": "kebo117",
    # "54": "kebo118",
    # "55": "kebo119",
    # "56": "lebo101",
    # "57": "lebo102",
    # "58": "lebo103",
    # "59": "lebo104",
    # "60": "lebo105",
    # "61": "lebo106",
    # "62": "lebo107",
    # "63": "lebo108",
    # "64": "lebo109",
    # "65": "lebo110",
}


def get_correct_option(question):
    options = question["options"]
    for option in options:
        if option["is_correct"]:
            return option["description"]

    return "no answer"

def create_question_material(question):
    prompt = f"""
    Prepare a short reading material about the given question including key details and explanations.
The content should directly address the following question:

**Question:** {question['description']}
**Answer:** {get_correct_option(question)}

Focus on delivering both the explanation of the {question["keywords"]} and the answer.


**Output as html**"""
    response = model.generate_content(prompt)
    print(response.text)

    prompt=f"""
    html: {response.text}

    split the html into sections with relevant subheadings to organize ideas clearly.
    add <hr> between each section
    """
    response = model.generate_content(prompt)
    question["content_html"] = get_html_from_response(response.text)

    html = get_html_from_response(response.text)
    
    return html

def create_question_material_from_search(question, ncert_sentence_wise_embeddings):
    fact = generate_fact_from_question(question)
    top_ncert_matches = search_pdf_top_sentences(ncert_sentence_wise_embeddings, fact)
    content = create_reading_material_content(fact, top_ncert_matches[0])
    question["content"] = content

    prompt = f""" **convert the response from llm to a html format**:
    {content}
    """
    response = model.generate_content(prompt)
    print(response.text)

    prompt=f"""
    html: {response.text}

    split the html into sections with relevant subheadings to organize ideas clearly.
    add <hr> between each section
    """
    response = model.generate_content(prompt)
    question["content_html"] = get_html_from_response(response.text)

def create_question_material_from_gemini(question, ncert_content_path):
    
    content = question["content"]
    prompt = f"""
    question: {question["description"]}
    options: {get_correct_option(question)}
    correct answer: {get_correct_option(question)}

    explain the below content in plain english, making it easy to understand and to be able to answer the given question.
    **Skip any part where the question and answer is discussed**
    **Do not use any image or figure as a reference in the content**
    
    {content}
    """
    response = model.generate_content(prompt)
    content = response.text
    question["new_content"] = content

    prompt = f""" **convert the response from llm to a html format**:
    {content}
    """
    response = model.generate_content(prompt)
    print(response.text)

    prompt=f"""
    html: {response.text}

    split the html into sections with relevant subheadings to organize ideas clearly.
    add <hr> between each section
    """
    response = model.generate_content(prompt)
    question["content_html"] = get_html_from_response(response.text)

def create_question_material_from_gemini1(question, ncert_content):
    content = get_ncert_content_gemini(ncert_content, question)
    question["content"] = content

    prompt = f""" **convert the response from llm to a html format**:
    {content}
    """
    response = model.generate_content(prompt)
    print(response.text)

    prompt=f"""
    html: {response.text}

    split the html into sections with relevant subheadings to organize ideas clearly.
    add <hr> between each section
    """
    response = model.generate_content(prompt)
    question["content_html"] = get_html_from_response(response.text)
    


def create_reading_material(json_path, ncert_content_path):

    quiz = read_json_file(json_path)

    call_collection_with_threading(
        func=create_question_material_from_gemini,
        args=(ncert_content_path,),
        threads=20,
        collection=quiz["questions"]
    )

    write_json_file(json_path, quiz)

def read_txt_file(path):
    with open(path, "r") as f:
        return f.read()

def combine_strings(strings, n):
    combined_strings = []
    for i in range(0, len(strings), n):
        combined_strings.append("\n\n\n\n\n".join(strings[i:i+n]))
    return combined_strings
    

def create_reading_material_content(json_path, ncert_content_folder_path):
    ncert_content_pages_path = filter_files(sorted(os.listdir(ncert_content_folder_path)), ".txt")
    ncert_content_pages = [read_txt_file(os.path.join(ncert_content_folder_path, page)) for page in ncert_content_pages_path]
    ncert_content_pages_group = combine_strings(ncert_content_pages, 3)

    for ncert_content in ncert_content_pages_group:
        create_pre_reading_material(json_path, ncert_content)
        find_unanswerable_content(json_path)

    find_unanswerable_content(json_path, repopulate=True)
    find_unanswerable_content(json_path)

def create_pre_reading_material(json_path, ncert_content):
    quiz = read_json_file(json_path)

    call_collection_with_threading(
        func=get_ncert_content_gemini,
        args=(ncert_content,),
        threads=20,
        collection=quiz["questions"]
    )

    write_json_file(json_path, quiz)



for quiz_id in quiz_id_to_pdf_map:
    json_path = f"/Users/pranav/GitHub/pdf-parsing/gemini/Neet/{quiz_id}.json"
    ncert_pdf_path = f"/Users/pranav/GitHub/pdf-parsing/gemini/Neet/ncert_books/biology/{quiz_id_to_pdf_map[quiz_id]}.pdf"
    ncert_pdf = upload_file_to_gemini(ncert_pdf_path)
    populate_question_keywords(json_path, ncert_pdf)

    ncert_content_path = parse_pdf(ncert_pdf_path)
    ncert_content_folder_path = ncert_content_path[:-4]
    create_reading_material_content(json_path, ncert_content_folder_path)
    create_reading_material(json_path, ncert_content_path)    
    print("created reading material")
    
    highlight_keywords(json_path)
    highlight_background_all(json_path)
    # clean_reading_material(json_path)

