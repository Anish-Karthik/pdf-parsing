from gemini_utilities import *
import random
import fitz  # PyMuPDF
from sentence_transformers import SentenceTransformer, util


class SentenceWiseEmbeddings:
    def __init__(self, sentence_embedding, sentence, pdf_pg_index):
        self.sentence_embedding = sentence_embedding
        self.sentence = sentence
        self.pdf_pg_index = pdf_pg_index

class NCERTContentMetadata:
    def __init__(self, pdf_pg_indices, raw_ncert_content, score):
        self.pdf_pg_indices = pdf_pg_indices
        self.raw_ncert_content = raw_ncert_content
        self.score = score

def get_correct_option(question):
    options = question["options"]
    for option in options:
        if option["is_correct"]:
            return option["description"]

    return "no answer"


def get_all_options(question):
    options = question["options"]
    return [option["description"] for option in options]


def content_keyword():
    neet_pdf = upload_file_to_gemini("/Users/pranav/GitHub/pdf-parsing/gemini/Neet/ncert_books/biology/kebo120.pdf")
    modules_raw = get_response_delayed_prompt(["Split the chapter from the pdf into smaller modules so that i can study with better understanding, give all the module headings", neet_pdf])
    modules = change_response_to_list(modules_raw)
    print(modules)

    contents = []
    for module in modules[1:2]:

        print(module)
        prompt = f"""help me learn this {module}, keep me engaged so that i understand, prepare a content about {module} using the above pdf so that i will be able to learn it later"""
        content = get_response_delayed_prompt([prompt, neet_pdf])

        prompt = f"""Give all the important words and keywords from the content"""
        keywords_raw = get_response_delayed_prompt(prompt + content)
        keywords = change_response_to_list(keywords_raw)

        print(keywords)
        print(content)


def get_random(list, n):
    return list[8:9]
    random.seed(None)
    random.shuffle(list)
    return list[:n]


def generate_fact_from_question(question):
    prompt = f"""
    question:{question["description"]}
    options:{get_all_options(question)}
    answer:{get_correct_option(question)}

    state this question as a fact."""
    return get_response_delayed_prompt(prompt)

def get_sentence_wise_embeddings(pdf_path) -> list[SentenceWiseEmbeddings]:
    with fitz.open(pdf_path) as pdf_file:
        sentence_wise_embeddings = []
        for page_num, page in enumerate(pdf_file):
            text = page.get_text()
            sentences = text.split(". ")  # Adjust this if your PDF uses different punctuation
            for sentence in sentences:
                sentence_embedding = model.encode(sentence, convert_to_tensor=True)
                sentence_wise_embeddings.append(SentenceWiseEmbeddings(sentence_embedding, sentence, page_num))
    return sentence_wise_embeddings

def get_question_by_id(id, questions):
    return next((q for q in questions if q["id"] == id), None)

def get_tamil_content_gemini(pdf_text, questions, ids):
    questions_in_prompt = ""
    for id in ids:
        question = get_question_by_id(id, questions)
        questions_in_prompt += f"question: {question['description']}\noptions: {get_all_options(question)}\ncorrect answer: {get_correct_option(question)}\n\n"
        
    prompt = f"""

    create a reading material to answer the given questions from the given content
    **Skip the last part where the question and answer is discussed**
    **Do not use any image or figure as a reference in the content**
    **The output should be in tamil language**
    

    questions:
    {questions_in_prompt}

    content:
    {pdf_text}
    
    """
    return get_response_delayed_prompt(prompt)

def merge_chunks(chunks, n):
    merged_chunks = []
    for i in range(0, len(chunks), n):
        merged_chunks.append(" ".join(chunks[i : max(i + n, len(chunks))]))
    return merged_chunks
    

def get_ncert_content_gemini(question, ncert_content):

    if "is_answerable" in question and question["is_answerable"] == True:
        return

    
    prompt = f"""
    question: {question["description"]}
    options: {"\n".join(get_all_options(question))}
    correct answer: {get_correct_option(question)}

    create a complete reading material from the given content to directly answer the given question and answer it.
    *Structure the reading material*

    
    **Skip the last part where the question and answer is discussed**
    **Do not use any image or figure as a reference in the content**

    content:
    {ncert_content}
    
    """
    response1 = model.generate_content(prompt)
    
    question["content"] = response1.text
    return

def belongs_to_range(range,n):
    return n>=range[0]-4 and n<=range[1]+4

def group_nearby_matches(top_matches) -> list[NCERTContentMetadata]:
    top_matches_grouped = []
    top_matches_metadata : list[NCERTContentMetadata] = []
    top_matches = top_matches[:15]
    top_matches = sorted(top_matches, key=lambda x: x[1])

    for match in top_matches:
        added = False
        for group in top_matches_grouped:
            if belongs_to_range(group[0], match[1]):
                group[0] = [min(group[0][0], match[1]), max(group[0][1], match[1])]
                group[1].append(match)
                added = True
                break
        if not added:
            top_matches_grouped.append([[match[1], match[1]], [match]])

    for group in top_matches_grouped:
        raw_ncert_content = ""
        pdf_indices = set()
        score = 0

        group[1] = sorted(group[1], key=lambda x: x[1])
        for match in group[1]:
            metadata: NCERTContentMetadata = match[0]
            raw_ncert_content += "\n" + metadata.raw_ncert_content
            # Convert single index to list before adding to set
            if isinstance(metadata.pdf_pg_indices, int):
                pdf_indices.add(metadata.pdf_pg_indices)
            else:
                pdf_indices.update(metadata.pdf_pg_indices)
            score = max(score, metadata.score)
            
        top_matches_metadata.append(
            NCERTContentMetadata(sorted(list(pdf_indices)), raw_ncert_content.strip(), score)
        )

    top_matches_metadata = sorted(top_matches_metadata, key=lambda x: x.score, reverse=True)
        
    return top_matches_metadata


def search_pdf_top_sentences(sentence_wise_embeddings, search_query, top_n=1) -> list[NCERTContentMetadata]:
    # Initialize the list before using it
    top_matches_with_index = []
    query_embedding = model.encode(search_query, convert_to_tensor=True)

    for index, sentence_embedding in enumerate(sentence_wise_embeddings):
        score = util.cos_sim(query_embedding, sentence_embedding.sentence_embedding).item()
        top_matches_with_index.append((NCERTContentMetadata([sentence_embedding.pdf_pg_index], sentence_embedding.sentence, score), index))
    
    # Move sorting outside the loop for better performance
    top_matches_with_index = sorted(top_matches_with_index, key=lambda x: x[0].score, reverse=True)
    top_matches: list[NCERTContentMetadata] = group_nearby_matches(top_matches_with_index)
        
    return top_matches[:top_n]

def print_questions_and_options(questions):
    for question in questions:
        print(question["description"])
        for option in question["options"]:
            print(option["description"])
        print("\n\n\n\n\n")


def print_correct_answers(questions):
    print("correct answer")
    for question in questions:
        print(get_correct_option(question))


def material(neet_pdf, neet_pdf_path):
    # Load and get random questions
    quiz = read_json_file("/Users/pranav/GitHub/pdf-parsing/gemini/Neet/31.json")
    random_questions = get_random(quiz["questions"], 5)

    # Generate and print reading materials
    for question in random_questions:
        
        # fact = generate_fact_from_question(question)
        # print("fact: ", fact)
        print("\n\n\n\n")
        ncert_content = get_ncert_content_gemini(neet_pdf, question)
        print("NCERT CONTENT gemini: \n\n\n", ncert_content)
        print("\n\n\n\n")
        # top_ncert_matches = search_pdf_top_sentences(ncert_sentence_wise_embeddings, fact)
        # print("pdf page number: ", top_ncert_matches[0].pdf_pg_indices)
        # print(top_ncert_matches[0].raw_ncert_content)
        # content = create_reading_material_content(fact, top_ncert_matches[0])
        # question["material"] = content
        # print(content)
        # print("\n\n\n\n")
        # print(question["description"])
        # print(get_all_options(question))
        # print("\n")
        # print(get_correct_option(question))
        # print("\n\n\n\n")

    print("\n\n\n\n")

    # Print questions and answers
    # print_questions_and_options(random_questions)
    # print("\n\n\n\n")
    # print_correct_answers(random_questions)


# model = SentenceTransformer('all-MiniLM-L6-v2')
# neet_pdf_path = "/Users/pranav/GitHub/pdf-parsing/gemini/Neet/ncert_books/biology/kebo101.pdf"
# # ncert_sentence_wise_embeddings: list[SentenceWiseEmbeddings] = get_sentence_wise_embeddings(neet_pdf_path)
# # neet_pdf = upload_file_to_gemini(neet_pdf_path)
# ncert_pdf_path = "/Users/pranav/GitHub/pdf-parsing/gemini/Neet/ncert_books/biology/kebo101/kebo101.txt"
# with open(ncert_pdf_path, "r") as f:
#     ncert_pdf = f.read()
# material(ncert_pdf, neet_pdf_path)
