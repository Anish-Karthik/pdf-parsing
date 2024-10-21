import json
from gemini_utilities import *
from question_keyowrd import *
from highlight_keywords import *
import markdown
import threading


quiz_id_to_pdf_map = {
    "51": "115",
}


def get_correct_option(question):
    options = question["options"]
    for option in options:
        if option["is_correct"]:
            return option["description"]

    return "no answer"


def create_page_content(question, neet_pdf):
    keywords = question["keywords"]

    # prompt = f"""prepare a content about {keywords} so that i will be able to answer this
    # The prepared content should be 100-150 words.
    # question:{question["description"]}
    # answer:{get_correct_option(question)}"""
    # page_content = model.generate_content([prompt, neet_pdf])
    # print(page_content.text)

    prompt = f"""prepare a content about {keywords} so that i will be able to answer this
    The prepared content should be 100-150 words.
    Get to the point. Make sure the content is clear and concise.
    Skip any introductions that are not relevant to the topic.
    
    make the content engaging and easy to read for better understanding. also make sure the content has the answer for
    question:{question["description"]}
    answer:{get_correct_option(question)}
    without giving the questions explicitly"""
    page_content = model.generate_content([prompt, neet_pdf])
    print(page_content.text)

    question["content_html"] = markdown.markdown(page_content.text)


def create_reading_material(json_path, neet_pdf):
    
    quiz = read_json_file(json_path)

    call_collection_with_threading(
        func=create_page_content,
        args=(neet_pdf,),
        threads=10,
        collection=quiz["questions"]
    )

    write_json_file(json_path, quiz)


for quiz_id in quiz_id_to_pdf_map:
    json_path = f"/Users/pranav/GitHub/pdf-parsing/gemini/Neet/{quiz_id}_copy.json"
    neet_pdf = upload_file_to_gemini(f"/Users/pranav/GitHub/pdf-parsing/gemini/Neet/ncert_books/biology/kebo{quiz_id_to_pdf_map[quiz_id]}.pdf")
    populate_question_keywords(json_path, neet_pdf)
    create_reading_material(json_path, neet_pdf)
    highlight_keywords(json_path)
