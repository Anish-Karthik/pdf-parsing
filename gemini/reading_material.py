from gemini_api import *
import re
import pandas as pd
import time
from google.api_core.exceptions import ResourceExhausted
import threading


def get_prompt(quiz_info, topic):
    return f"""
    input: {quiz_info}
    topic: {topic}

    Narrate all the input provided above like a book with additional example and different paragraph etc.
    The output should be in Tamil.
    Do not remove any content from the input.
    Give a title for each statement in the input content.
    Make the content as detailed as possible.
    Make sure the content is relevant without any error.
    """


api_key = os.environ.get("GEMINI_API_KEY")
configure_client(api_key)

model = generativeai.GenerativeModel(
    model_name="models/gemini-1.5-pro"
)


input_file_path = "/home/barath/Documents/tamil/19-தன்வினை, பிறவினை, செய்வினை, செயப்பாட்டுவினை.json"
output_file_path = "/home/barath/Documents/tamilMaterial/19-தன்வினை, பிறவினை, செய்வினை, செயப்பாட்டுவினை.json"
detailed_solution = []
with open(input_file_path, 'r') as f:
    quiz = json.load(f)
    for question in quiz["questions"]:
        if question["detailed_solution"] is not None and len(question["detailed_solution"]) > 0:
            detailed_solution.append(question["detailed_solution"])

    prompt = get_prompt(detailed_solution, quiz["topic"])
    response = model.generate_content(prompt)

with open(output_file_path, "w") as f:
    json.dump(response.text, f, indent=4)
