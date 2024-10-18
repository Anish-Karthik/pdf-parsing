import json
from gemini_utilities import *


# neet_pdf = upload_file_to_gemini("/Users/pranav/GitHub/pdf-parsing/gemini/Neet/ncert_books/biology/kebo120.pdf")
# print(neet_pdf.name)
neet_pdf = generativeai.get_file("files/ksodcmmmmojq")
# neet_pdf = extract_text_from_pdf("/Users/pranav/GitHub/pdf-parsing/gemini/Neet/ncert_books/biology/kebo120.pdf")


def get_page_content(keywords,questions):
    global neet_pdf

    chat = model.start_chat(history=[])
    prompt = f"""help me learn in detailed about {keywords}, prepare a content about {keywords} using the above pdf so that i will be able to learn it later"""
    page_content = chat.send_message([prompt, neet_pdf])
    print(page_content.text)
    prompt = f"""make the content more engaging. also make sure the content has the answer for {questions} without giving the questions explicitly"""
    page_content = chat.send_message([prompt, neet_pdf])

    print(page_content.text)


keywords = [
  "sarcomere",
  "myosin",
  "H-zone",
  "relaxed state",
  "muscle contraction",
  "Actin",
  "thick filaments",
  "Z-lines",
  "M-line",
]

questions = [
  "Which proteins will be included in H-zone of myofilaments if sarcomere is in relaxed state?"
]
get_page_content(keywords,questions)