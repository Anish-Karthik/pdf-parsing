import json
from gemini_utilities import *
from question_keyowrd import *
from highlight_keywords import *
import markdown
import threading


quiz_id_to_pdf_map = {
    "35": "101",
    # "38": "102",
    # "39": "103",
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

    prompt = f"""
    Prepare content about {keywords}, including key details and explanations to help students understand the topic thoroughly.
The content should also directly address the following and also exploring similar questions:

**Question:** {question['description']}
**Answer:** {get_correct_option(question)}

The content should also be able to answer atleast 5 questions related to the topic.

Ensure the content is concise (100-150 words), engaging, and clear. Avoid unnecessary introductions.
Focus on delivering both the explanation of the {keywords} and the answer in a way that helps students easily grasp and retain the information."""
    page_content = model.generate_content([prompt, neet_pdf])
    html_content = markdown.markdown(page_content.text)

    prompt = f"""
Using the following content:
{html_content}

Create a summary that is both appealing and stimulating, using the following format:

1. **Subheadings**: Divide the content into sections with relevant subheadings to organize ideas clearly.
2. **Bullet Points**: Use bullet points to present key facts, concepts, or steps in a structured way.
3. **Bold Key Terms**: Highlight important terms or concepts in bold to make them stand out.
4. **Engaging Language(Simple)**: Use language that sparks curiosity and encourages the reader to explore more and very simple
5. **Short Sentences**: Ensure sentences are short, punchy, simple, and to the point, making the content easier to digest and more memorable.

The final summary should:
- Be concise (around 100-150 words).
- Use the above formatting to make it visually engaging and easy to read.
- Include elements that ignite curiosity and leave the reader wanting to explore further.
- skip any introductions
"""
    page_content = model.generate_content(prompt)
    
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
