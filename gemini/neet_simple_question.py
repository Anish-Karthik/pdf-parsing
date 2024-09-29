from gemini_api import *
import re
import pandas as pd
import time
from google.api_core.exceptions import ResourceExhausted
import threading

output = 0


def get_correct_option(question):
    options = question["options"]
    for option in options:
        if option["is_correct"]:
            return option["description"]

    return "no answer"


def filter_response(text):
    text = re.sub("\\*{2,}", "", text)
    return text[text.index("["):text.rindex("]") + 1]


def get_question_prompt(topic, question):
    return f"""
    <question>
        <description>{question["description"]}</description>
        <answer>{get_correct_option(question)}</answer>
    </question>
    Step 1:
    Create a similar question as above with reduced difficulty possible. The new question should not exactly be the same as the above question but very similar.
    The new question should be easy for a student to learn the topic '{topic}'. It should also be easy to read and **not verbose**

    Step 2: Solve the question generated. Create step by step detailed solution and provide the same as reasoning for the answer. Verify that each step is correct in the reasoning.

    """ + """
      Output:
      give json format
        {
            "question": question_description,
            "reasoning": reasoning
        }
  """


def get_options_prompt(question_response):
    return f"""
    <question>
        {question_response}
    </question>
    Task:
    Identify the correct option based on the reasoning and create 4 options in which one is correct.
    Verify the correctness of the options.

    <rules>
        1. Option should not verbose. It should usually be one word or number, may be followed by unit.
    </rules>
    """ + """
      Output:
      give json format
        {
            "options":[
                option1,
                option2,
                option3,
                option4
            ],
            "correct_option":("A" or "B" or "C" or "D"),
        }
  """


def get_simple_question(topic, question):
    try:
        question_output = {}
        prompt = get_question_prompt(topic, question)
        response = model.generate_content(prompt)
        question_output["original_question"] = question["description"]
        question_output["id"] = question["id"]
        question_output["question"] = response.text

        option_response = model.generate_content(get_options_prompt(response.text))
        question_output["option"] = option_response.text

        question_json = json.loads(response.text)
        question_json.update(json.loads(option_response.text))
        question_json["original_question"] = question["description"]
        question_json["id"] = question["id"]
        solution_json.append(question_json)

        print(question["id"])
    except ResourceExhausted as e:
        print(e)
    except Exception as e:
        solution.append(question_output)
        print(e)


api_key = os.environ.get("GEMINI_API_KEY")
configure_client(api_key)

model = generativeai.GenerativeModel(
    model_name="models/gemini-1.5-flash"
)


def split_into_batches(array, batch_size=5):
    return [array[i:i + batch_size] for i in range(0, len(array), batch_size)]


for number in range(20, 166):
    input_file_path = f"""/home/barath/Documents/Neet/{number}.json"""
    output_file_path = f"""/home/barath/Documents/NeetSimple/{number}.json"""
    output_parsed_file_path = f"""/home/barath/Documents/NeetSimple/parsed-{number}.json"""
    solution = []
    solution_json = []
    with open(input_file_path, 'r') as f:
        quiz = json.load(f)

        question_batches = split_into_batches(quiz["questions"], 20)
        for question_batch in question_batches:
            threads = []
            for question in question_batch:
                thread = threading.Thread(target=get_simple_question, args=(quiz["topic"], question))
                threads.append(thread)
                thread.start()
            for thread in threads:
                thread.join()

    with open(output_file_path, "w") as f:
        json.dump(solution, f, indent=4)

    with open(output_parsed_file_path, "w") as f:
        json.dump(solution_json, f, indent=4)
