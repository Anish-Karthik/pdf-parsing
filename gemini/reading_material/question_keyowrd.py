
import json
import os
import threading
import google.generativeai as generativeai
from google.api_core.exceptions import ResourceExhausted
import pandas as pd
from gemini_utilities import *
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer


def get_prompt(qn, correct_option, topic):
    return f"""
    question: {qn}
    answer: {correct_option}

    The question belongs to the topic 'Biology - {topic}' from NCERT book.

    Give top 5 keywords for the question to prepare on the topic to understand the question better.

    output: **Return the keywords as an array of strings**
    """


def get_correct_option(question):
    options = question["options"]
    for option in options:
        if option["is_correct"]:
            return option["description"]

    return "no answer"


def get_json_response(response):
    text = response.text
    text = text.replace("```json", "")
    text = text.replace("```", "")
    return json.loads(text)


def get_question_keywords(question, topic, retry=0):
    try:
        response = model.generate_content(
            get_prompt(question["description"], get_correct_option(question), topic))

        print(question["id"])
        print(question["description"])
        print(get_correct_option(question))

        keywords = response.text
        keywords = keywords.replace("```json", "")
        keywords = keywords.replace("```", "")
        try:
            get_json_response(response)

            question["keywords"] = get_json_response(response)
        except Exception as e:
            if retry == 3:
                return
            return get_question_keywords(question, topic, retry + 1)
    except ResourceExhausted as e:
        print(e)
        return get_question_keywords(question, topic)
    except Exception as e:
        print(e)


api_key = os.environ.get("GEMINI_API_KEY")
generativeai.configure(api_key=api_key)

model = generativeai.GenerativeModel(
    model_name="models/gemini-1.5-flash"
)


def split_into_batches(array, batch_size=5):
    return [array[i:i + batch_size] for i in range(0, len(array), batch_size)]


def populate_question_keywords():
    input_file_path = f"""/home/barath/Documents/Neet/53.json"""
    with open(input_file_path, 'r') as f:
        quiz = json.load(f)
        question_batches = split_into_batches(quiz["questions"], 5)
        for question_batch in question_batches:
            threads = []
            for question in question_batch:
                thread = threading.Thread(target=get_question_keywords, args=(question, quiz["topic"]))
                threads.append(thread)
                thread.start()
            for thread in threads:
                thread.join()

    with open(input_file_path, "w") as f:
        json.dump(quiz, f, indent=4)


def cluster_keywords():
    input_file_path = f"""/home/barath/Documents/sat/code/pdf-parsing/gemini/Neet/53.json"""
    keywords = []
    questions = []
    with open(input_file_path, 'r') as f:
        quiz = json.load(f)

        for question in quiz["questions"]:
            keywords += question["keywords"]
            questions.append({"question": question["description"], "answer": get_correct_option(question)})

    keywords = list(set(keywords))

    # Create a TF-IDF vectorizer to convert keywords to numerical features
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(keywords)

    # Apply K-means clustering
    kmeans = KMeans(n_clusters=40)  # Adjust the number of clusters as needed
    kmeans.fit(X)

    # Get the cluster labels for each keyword
    labels = kmeans.labels_

    # Create buckets of keywords based on the labels
    buckets = {}
    for i, label in enumerate(labels):
        if label not in buckets:
            buckets[label] = []
        buckets[label].append(keywords[i])

    # Print the buckets
    for label, keywords in buckets.items():
        print(f"Cluster {label}: {keywords}")


def consolidate_keywords():
    input_file_path = f"""/home/barath/Documents/sat/code/pdf-parsing/gemini/Neet/53.json"""
    keywords = []
    questions_with_options = []
    questions = []
    with open(input_file_path, 'r') as f:
        quiz = json.load(f)

        for question in quiz["questions"]:
            options = ""
            for option in question["options"]:
                options += (option["description"] + " ")
            keywords += question["keywords"]
            questions_with_options.append(
                {"id": question["id"], "question": question["description"], "options": options, "answer": get_correct_option(question)})
            questions.append(
                {"id": question["id"], "question": question["description"]})

    # keywords = list(set(keywords))

    # print(keywords)
    # return

    # print(len(keywords))

    chat = model.start_chat(history=[])

    # neet_pdf = upload_file_to_gemini("/home/barath/Documents/Neet Books/kebo1dd/kebo117.pdf")
    neet_pdf = generativeai.get_file("files/wm9cvlcyhc0d")
    print(neet_pdf.name)

    prompt = f"""
    questions:{questions_with_options}
    Understand each question and also the keywords involved in the question.
    Group the questions based on the technical knowledge required to answer these questions.
    **Each bucket must contain maximum of 5 questions only**
    Verify and make sure that each bucket contains no more than 5 questions.
    """
    response = chat.send_message([prompt, neet_pdf])
    print(response.text)

    # return
    # prompt = f"""
    # questions: {questions}
    # keywords: {keywords}
    # From the above buckets/groups assign all the questions to buckets, assign the relevant keywords to each bucket from the above keywords.
    # """
    # response = chat.send_message(prompt)

    # prompt = "remove the groups which are very similar to other groups"
    # response = chat.send_message(prompt)

    prompt = f"""
    Format the above content as json"""
    response = chat.send_message(prompt)

    print(get_json_response(response))

    output_file_path = f"""/home/barath/Documents/sat/code/pdf-parsing/gemini/Neet/53_question_keyword_map.json"""
    with open(output_file_path, "w") as f:
        json.dump(get_json_response(response), f, indent=4)


consolidate_keywords()
