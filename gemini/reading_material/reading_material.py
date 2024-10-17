import json
from gemini_utilities import *


neet_pdf = upload_file_to_gemini("/Users/pranav/GitHub/pdf-parsing/gemini/Neet/ncert_books/biology/kebo120.pdf")


def get_page_content(keywords,questions):
    global neet_pdf

    chat = model.start_chat(history=[])
    prompt = f"""help me learn in detailed about {keywords}, prepare a content about {keywords} using the above pdf so that i will be able to learn it later"""
    page_content = chat.send_message([prompt, neet_pdf])
    prompt = f"""make the content more engaging like a story rather than points"""
    page_content = chat.send_message(prompt)
    prompt = f"""Make sure the reading the content makes the questions {questions} answerable"""
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