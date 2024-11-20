from clean_reading_material import clean_reading_material
from gemini_utilities import *
# from question_keyowrd import *
from content_keyword import *
from highlight_keywords import *
from parse_pdf import parse_pdf
from question_keyowrd import populate_question_keywords_tamil


quiz_id_to_pdf_map = {
    "169-சிலப்பதிகாரம், மணிமேகலை.json": "6th_Std_Tamil_CBSE-180-183.pdf"
}

def get_python_code_from_response(response):
    return response[response.find("```python")+9:response.rfind("```")]

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
    except:
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

def get_question_by_id(id, quiz):
    return next((q for q in quiz["questions"] if q["id"] == id), None)

def create_pre_reading_material_from_gemini(ids, tamil_content, quiz):
    content = get_tamil_content_gemini(tamil_content, quiz["questions"], ids)
    prompt = f""" **convert the response from llm to a html format**:
    {content}
    """
    response = model.generate_content(prompt)
    print(response.text)
    prompt=f"""
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

    prompt=f"""
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



for quiz_id in quiz_id_to_pdf_map:
    print("tamil reading material")
    json_path = f"/Users/pranav/GitHub/pdf-parsing/gemini/tamil/{quiz_id}"
    tamil_pdf_path = f"/Users/pranav/GitHub/pdf-parsing/qgen/generated/{quiz_id_to_pdf_map[quiz_id]}"
    populate_question_keywords_tamil(json_path, tamil_pdf_path)
    # print("populated tamil question keywords")
    groups_with_ids = group_questions_tamil(json_path)
    # print("grouped tamil questions")
    tamil_content = parse_pdf(tamil_pdf_path)
    create_pre_reading_material(json_path, tamil_content, groups_with_ids)
    create_reading_material(json_path, tamil_content, groups_with_ids)
    # print("created reading material")
    highlight_keywords(json_path)
    highlight_background_all(json_path)
    clean_reading_material(json_path)

    
