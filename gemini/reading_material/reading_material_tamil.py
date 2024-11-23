from clean_reading_material import clean_reading_material
from gemini_utilities import *
# from question_keyowrd import *
from content_keyword import *
from highlight_keywords import *
from parse_pdf import parse_pdf
from question_keyowrd import populate_question_keywords_tamil
import pandas as pd

quiz_id_to_topic_map = {
    "169-சிலப்பதிகாரம், மணிமேகலை.json": "சிலப்பதிகாரம், மணிமேகலை"
}


def find_all_pages_for_topic(csv_path, topic):
    csv_file = pd.read_csv(csv_path)
    pages = []
    for _, row in csv_file.iterrows():
        start = row["start page"]
        end = row["end page"]
        topic_name = str(row["topic name"]) if pd.notna(row["topic name"]) else ""
        if topic in topic_name or topic_name in topic and pd.notna(start) and pd.notna(end) and topic_name != "":
            pages.append(str(start) + "-" + str(end))
    return pages


def get_all_pdf_paths_for_topic(topic) -> list[str]:
    csv_paths_dir = "/Users/pranav/GitHub/pdf-parsing/gemini/reading_material/tamil_pdf_map"
    csv_paths = os.listdir(csv_paths_dir)
    pdf_paths = []
    for csv_path in sorted(csv_paths):
        start_end_list = find_all_pages_for_topic(os.path.join(csv_paths_dir, csv_path), topic)
        for start_end in start_end_list:
            pdf_path = f"/Users/pranav/GitHub/pdf-parsing/qgen/generated/{csv_path.removesuffix(".csv")}th-{start_end}.pdf"
            pdf_paths.append(pdf_path)
    return pdf_paths


def get_python_code_from_response(response):
    return response[response.find("```python") + 9:response.rfind("```")]


def filter_response_into_groups(response):
    prompt = f"""
    From this response about grouped questions, extract just the question IDs for each group and format them as a list of lists.
    Each inner list should contain the IDs for one group.

    Response:
    {response}

    Output format example:
    [[1, 2, 3], [4, 5], [6, 7, 8]]

    Return only the list, no other text.
    """

    group_response = model.generate_content(prompt)
    print(group_response.text)
    # Convert string representation of list to actual list
    try:
        if "```python" in group_response.text:
            filtered_response = get_python_code_from_response(group_response.text)
            print("filtered response", filtered_response)
            return eval(filtered_response)
        else:
            return eval(group_response.text)
    except BaseException:
        print("Error parsing groups response")
        return []


def group_questions_tamil(json_path):
    quiz = read_json_file(json_path)
    questions_in_prompt = ""
    for question in quiz["questions"]:
        questions_in_prompt += f"""
        id: {question['id']}
        question: {question['description']}
        keywords: {question['keywords']}







        """
    prompt = f"""

    Group the following questions based on their keywords and topics into meaningful sections.
    Each section should have a clear theme or concept that connects the questions.

    For each section:
    1. Give a suitable heading that captures the main theme
    2. List the question IDs that belong to that section
    3. Explain briefly why those questions are grouped together

    Questions:
        {questions_in_prompt}
    """
    response = model.generate_content(prompt)

    groups_with_ids = filter_response_into_groups(response.text)
    return groups_with_ids


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

    prompt = f"""
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

    prompt = f"""
    html: {response.text}

    split the html into sections with relevant subheadings to organize ideas clearly.
    add <hr> between each section
    """
    response = model.generate_content(prompt)
    question["content_html"] = get_html_from_response(response.text)


def get_question_by_id(id, quiz):
    return next((q for q in quiz["questions"] if q["id"] == id), None)

def create_pre_reading_material_from_gemini(ids, tamil_content, quiz):
    content = get_tamil_content_gemini(tamil_content, quiz["questions"], ids)
    prompt = f""" **convert the response from llm to a html format**:
    {content}
    """
    response = model.generate_content(prompt)
    print(response.text)
    prompt = f"""
    html: {response.text}

    split the html into sections with relevant subheadings to organize ideas clearly.
    add <hr> between each section
    **The content in it should be in tamil language**
    """
    response = model.generate_content(prompt)

    for id in ids:
        question = get_question_by_id(id, quiz)
        question["content"] = content
        question["content_html"] = get_html_from_response(response.text)


def create_question_material_from_gemini(group_with_ids, tamil_content, quiz):
    questions_in_prompt = ""
    for id in group_with_ids:
        question = get_question_by_id(id, quiz)
        questions_in_prompt += f"""
        question: {question["description"]}
        options: {get_correct_option(question)}
        correct answer: {get_correct_option(question)}



        """
    contents_in_prompt = ""
    for id in group_with_ids:
        question = get_question_by_id(id, quiz)
        contents_in_prompt += f"""
        {question["content"]}
        """

    prompt = f"""

    explain the below content in plain tamil, making it easy to understand and to be able to answer the given question.
    **Skip any part where the question and answer is discussed**
    **Do not use any image or figure as a reference in the content**

    Questions:
        {questions_in_prompt}

    Content:
    {contents_in_prompt}

    """
    response = model.generate_content(prompt)
    content = response.text

    prompt = f""" **convert the response from llm to a html format**:
    {content}
    """
    response = model.generate_content(prompt)
    print(response.text)

    prompt = f"""
    html: {response.text}

    split the html into sections with relevant subheadings to organize ideas clearly.
    add <hr> between each section
    """
    response = model.generate_content(prompt)

    for id in group_with_ids:
        question = get_question_by_id(id, quiz)
        question["material_id"] = group_with_ids[0]
        question["new_content"] = content
        question["content_html"] = get_html_from_response(response.text)


def create_pre_reading_material(json_path, tamil_content, groups_with_ids):
    quiz = read_json_file(json_path)

    call_collection_with_threading(
        func=create_pre_reading_material_from_gemini,
        args=(tamil_content, quiz),
        threads=10,
        collection=groups_with_ids
    )

    write_json_file(json_path, quiz)

def explain_content(text, meaning):
    prompt = f"""
    for every 2 lines in the poem:
     - give the 2 lines without any change in the content(in italic)
     - explain the 2 lines of poem in tamil based on the given meaning of the content in a detailed manner, easy for a student to understand
     - also give the meaning for complex words for each two lines.

    **The output should only contain tamil language**
    **Avoid any prefix or suffix about the generated content**
    Content:
    {text}

    meaning:
    {meaning}
    """
    response = model.generate_content(prompt)
    print(response.text)
    return response.text

def extract_meaning(text):
    prompt = f"""
        extract the meaning of the given prose/poem from the given text
        **Do not omit any content**
        **The output should only contain tamil language**
        **Avoid any prefix or suffix about the generated content**

        text:
        {text}
    """
    response = model.generate_content(text)
    return response.text

def split_into_chunks(text):
    prompt = f"""
    split the content into smaller chunks using the delimiter: </chunk>

    Content:
    {text}
    """
    response = model.generate_content(prompt)

    return clean_split(response.text,"</chunk>")
    return response.text

def get_readable_content(text_file_path : str):
    # text_file_path = "/Users/pranav/GitHub/pdf-parsing/qgen/generated/9th-78-81.txt"
    new_text_file_path = text_file_path[:-4] + "_readable.txt"
    meaning_text_file_path = text_file_path[:-4] + "_meaning.txt"

    # if os.path.exists(new_text_file_path):
    #     return
    
    text = read_txt_file(text_file_path)
    meaning = extract_meaning(text)
    write_txt_file(meaning_text_file_path, meaning)
    split_content = split_into_chunks(text)
    print(split_content)
    merged_content_readable = ""
    for content in split_content:
        merged_content_readable += "</chunk>" + explain_content(content, meaning)
        
    write_txt_file(new_text_file_path, merged_content_readable)
    # return response.text


def create_material_for_topic(topic, pdf_paths):
    for pdf_path in pdf_paths:
        text_file_path = parse_pdf(pdf_path)
        get_readable_content(text_file_path)
        print(f"parsed {pdf_path}")

def split_into_pages(text: str):
    text = text.replace("</chunk>","")
    prompt = f"""
    split the content into pages to keep the readers occupied using the delimiter:</page>
    **each page should be long**

    Content:
    {text}
    """
    response = model.generate_content(prompt)

    print(response.text)
    return clean_split(response.text, "</page>")

def create_topic_material_from_gemini(page_content, text_file_path):
    # prompt = f"""
    # make the below content structured, without omiting anything
    # content:
    # {page_content["content"]}
    # """
    # page_content["content"] = model.generate_content(prompt)
    prompt = f""" **convert the response from llm to a html format**:
    **the content should only be in tamil language**
    **make sure to use <em> whenever necessary**

    content:
    {page_content["content"]}
    """
    response = model.generate_content(prompt)
    print(response.text)

    prompt = f"""
    html: {response.text}

    split the html into many sections with relevant subheadings to organize ideas clearly.
    add <hr> between each section
    """
    response = model.generate_content(prompt)

    page_content["content_html"] = get_html_from_response(response.text)

def get_introduction(text):
    prompt=f"""
    prepare an introduction for the given content in tamil language, easy for a student to understand
    **The output should only contain tamil language**
    **Avoid any prefix or suffix about the generated content**

    Content:
    {text}
    """
    response = model.generate_content(prompt)
    return response.text

def create_reading_material_topic(text_file_path):
    text = read_txt_file(text_file_path)
    pages_content = split_into_pages(text)
    pages_content = [get_introduction(text)] + pages_content

    print("\n\n</page>\n\n".join(pages_content))

    pages_dicts = list() 
    for content in pages_content:
        t = dict()
        t["content"] = content
        pages_dicts.append(t)

    call_collection_with_threading(
        func=create_topic_material_from_gemini,
        args=(text_file_path,),
        threads=10,
        collection=pages_dicts
    )

    html_dir_path = "/Users/pranav/GitHub/pdf-parsing/gemini/tamil/reading_material"
    for i,page in enumerate(pages_dicts):
        html_file_path = os.path.join(html_dir_path,f"{i}.html")
        write_txt_file(html_file_path, page["content_html"])    
    

def create_reading_material(json_path, tamil_content, groups_with_ids):

    quiz = read_json_file(json_path)

    call_collection_with_threading(
        func=create_question_material_from_gemini,
        args=(tamil_content, quiz),
        threads=10,
        collection=groups_with_ids
    )

    write_json_file(json_path, quiz)


def read_txt_file(path):
    with open(path, "r") as f:
        return f.read()

import re

def change_name():
    dir_path = "/Users/pranav/GitHub/pdf-parsing/qgen/generated"
    pdf_paths = os.listdir(dir_path)
    for pdf_path in pdf_paths:
        pattern = r"(\d+th).*?-(\d+)-(\d+)"
        match = re.search(pattern, pdf_path)
        if not match:
            continue
        group = match.groups()
        new_name = f"{group[0]}-{group[1]}-{group[2]}.pdf"
        os.rename(os.path.join(dir_path, pdf_path), os.path.join(dir_path, new_name))

# change_name()
create_reading_material_topic("/Users/pranav/GitHub/pdf-parsing/qgen/generated/9th-78-81_readable.txt")



# get_readable_content("/Users/pranav/GitHub/pdf-parsing/qgen/generated/9th-78-81.txt")
# for quiz_id in quiz_id_to_topic_map:
#     # print("tamil reading material")
#     json_path = f"/Users/pranav/GitHub/pdf-parsing/gemini/tamil/{quiz_id}"
#     pdf_paths = get_all_pdf_paths_for_topic(quiz_id_to_topic_map[quiz_id])
    # create_material_for_topic(quiz_id_to_topic_map[quiz_id], pdf_paths)
    # tamil_pdf_path = f"/Users/pranav/GitHub/pdf-parsing/qgen/generated/{quiz_id_to_pdf_map[quiz_id]}"
    # populate_question_keywords_tamil(json_path, tamil_pdf_path)
    # # print("populated tamil question keywords")
    # groups_with_ids = group_questions_tamil(json_path)
    # # print("grouped tamil questions")
    # tamil_content = parse_pdf(tamil_pdf_path)
    # create_pre_reading_material(json_path, tamil_content, groups_with_ids)
    # create_reading_material(json_path, tamil_content, groups_with_ids)
    # # print("created reading material")
    # highlight_keywords(json_path)
    # highlight_background_all(json_path)
    # clean_reading_material(json_path)
