import json
from gemini_utilities import *
from question_keyowrd import *
from content_keyword import *
from highlight_keywords import *
import markdown
import threading


quiz_id_to_pdf_map = {
    "31": "101",
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

def create_question_material_from_gemini(question, ncert_content):
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
    


def create_reading_material(json_path, ncert_content):

    quiz = read_json_file(json_path)

    call_collection_with_threading(
        func=create_question_material_from_gemini,
        args=(ncert_content,),
        threads=10,
        collection=quiz["questions"]
    )

    write_json_file(json_path, quiz)

def read_txt_file(path):
    with open(path, "r") as f:
        return f.read()


for quiz_id in quiz_id_to_pdf_map:
    json_path = f"/Users/pranav/GitHub/pdf-parsing/gemini/Neet/{quiz_id}.json"
    neet_pdf_path = f"/Users/pranav/GitHub/pdf-parsing/gemini/Neet/ncert_books/biology/kebo{quiz_id_to_pdf_map[quiz_id]}.pdf"
    neet_pdf = upload_file_to_gemini(neet_pdf_path)
    populate_question_keywords(json_path, neet_pdf)
    print("populated question keywords...")
    
    # ncert_sentence_wise_embeddings: list[SentenceWiseEmbeddings] = get_sentence_wise_embeddings(neet_pdf_path)
    # print("got sentence wise embeddings...")

    ncert_pdf_path = "/Users/pranav/GitHub/pdf-parsing/gemini/Neet/ncert_books/biology/kebo101/kebo101.txt"
    ncert_content = read_txt_file(ncert_pdf_path)
    create_reading_material(json_path, ncert_content)
    print("created reading material...")
    
    highlight_keywords(json_path)

    
