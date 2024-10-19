import json
from gemini_utilities import *
import markdown
import threading


quiz_id_to_pdf_map = {
    "51": "115",
    "52": "116",
    "53": "117"
}


# neet_pdf = upload_file_to_gemini("/Users/pranav/GitHub/pdf-parsing/gemini/Neet/ncert_books/biology/kebo115.pdf")
# print(neet_pdf.name)
# neet_pdf = generativeai.get_file("files/2f37whdgjqik")
# neet_pdf = extract_text_from_pdf("/Users/pranav/GitHub/pdf-parsing/gemini/Neet/ncert_books/biology/kebo120.pdf")

def get_correct_option(question):
    options = question["options"]
    for option in options:
        if option["is_correct"]:
            return option["description"]

    return "no answer"


def get_page_content(question):
    keywords = question["keywords"]

    global neet_pdf

    prompt = f"""prepare a content about {keywords} so that i will be able to answer this
    question:{question["description"]}
    answer:{get_correct_option(question)}"""
    page_content = model.generate_content(prompt)
    print(page_content.text)

    prompt = f"""{page_content.text}
    Get to the point. Make sure the content is clear and concise.
    make the content engaging and easy to read for better understanding. also make sure the content has the answer for
    question:{question["description"]}
    answer:{get_correct_option(question)}
    without giving the questions explicitly"""
    page_content = model.generate_content(prompt)
    print(page_content.text)

    return page_content.text


def id_to_question(id, questions):
    for question in questions:
        if question["id"] == id:
            return question


reading_materials = []


def create_page_content(question):
    page_content = get_page_content(question)

    reading_material_page = {}
    reading_material_page["id"] = question["id"]
    reading_material_page["keywords"] = question["keywords"]
    reading_material_page["content"] = page_content

    reading_materials.append(reading_material_page)


def create_reading_material(json_path, quiz_id):
    with open(json_path, 'r') as f2:
        quiz = json.load(f2)

        threads = []

        for question_batch in split_into_batches(quiz["questions"], 10):
            for question in question_batch:
                thread = threading.Thread(target=create_page_content, args=(question,))
                threads.append(thread)
                thread.start()

            for thread in threads:
                thread.join()

        with open(f"/Users/pranav/GitHub/pdf-parsing/gemini/Neet/reading_material/{quiz_id}_reading_material.json", "w") as f:
            json.dump(reading_materials, f, indent=4)
            reading_materials = []


for quiz_id in quiz_id_to_pdf_map:
    json_path = f"/Users/pranav/GitHub/pdf-parsing/gemini/Neet/{quiz_id}.json"
    neet_pdf = upload_file_to_gemini(f"/Users/pranav/GitHub/pdf-parsing/gemini/Neet/ncert_books/biology/kebo{quiz_id_to_pdf_map[quiz_id]}.pdf")
    create_reading_material(json_path, quiz_id)
