import json
from gemini_utilities import *
import markdown


neet_pdf = upload_file_to_gemini("/Users/pranav/GitHub/pdf-parsing/gemini/Neet/ncert_books/biology/kebo115.pdf")
print(neet_pdf.name)
# neet_pdf = generativeai.get_file("files/ksodcmmmmojq")
# neet_pdf = extract_text_from_pdf("/Users/pranav/GitHub/pdf-parsing/gemini/Neet/ncert_books/biology/kebo120.pdf")

def get_correct_option(question):
    options = question["options"]
    for option in options:
        if option["is_correct"]:
            return option["description"]

    return "no answer"


def get_page_content(questions):
    keywords = []
    for question in questions:
        keywords += question["keywords"]
    keywords = list(set(keywords))

    questions_desc = []
    for question in questions:
        questions_desc.append({"question":question["description"], "answer":get_correct_option(question)})

    print(keywords)
    print(questions_desc)
    global neet_pdf

    prompt = f"""prepare a content about {keywords} so that i will be able to answer these questions {questions_desc}"""
    page_content = model.generate_content(prompt)
    print(page_content.text)
    prompt = f"""{page_content.text}
    Get to the point. Make sure the content is clear and concise.
    make the content engaging and easy to read for better understanding. also make sure the content has the answer for {questions_desc} without giving the questions explicitly"""
    page_content = model.generate_content(prompt)

    prompt = f"""{page_content.text}
    Hightlight the important data and keywords from the content in *Red*
    additional context:
    {questions_desc}
    output as html
    """
    page_content = model.generate_content(prompt)

    print(page_content.text)
    return page_content.text


# keywords = [
#   "sarcomere",
#   "myosin",
#   "H-zone",
#   "relaxed state",
#   "muscle contraction",
#   "Actin",
#   "thick filaments",
#   "Z-lines",
#   "M-line",
# ]

# questions = [
#   "Which proteins will be included in H-zone of myofilaments if sarcomere is in relaxed state?"
# ]
# get_page_content(keywords,questions)
def id_to_question(id,questions):
  for question in questions:
    if question["id"] == id:
      return question

reading_materials = []
def create_reading_material(json_map_path, json_path):
  with open(json_map_path, 'r') as f:
    with open(json_path, 'r') as f2:
      buckets = json.load(f)
      quiz = json.load(f2)
      
      for i,bucket in enumerate(buckets[:10]):
          questions = []
          for question in bucket["questions"]:
              questions.append(id_to_question(question["id"],quiz["questions"]))

          page_content = get_page_content(questions)
          reading_materials.append(page_content)
          with open(f"/Users/pranav/GitHub/pdf-parsing/gemini/Neet/reading_material/51.{i}.html", "w") as f:
              text = page_content
              f.write(text)
          

json_map_path = "/Users/pranav/GitHub/pdf-parsing/gemini/Neet/51_question_keyword_map.json"
json_path = "/Users/pranav/GitHub/pdf-parsing/gemini/Neet/51.json"
create_reading_material(json_map_path, json_path)

for i,reading_material in enumerate(reading_materials):
  with open(f"/Users/pranav/GitHub/pdf-parsing/gemini/Neet/reading_material/51.{i}.html", "w") as f:
    text = reading_material
    # text = text.replace("\\n", "\n")

    # html = markdown.markdown(text)

    f.write(text)