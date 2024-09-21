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


def get_subtopics(topic):
    try:
        prompt = f"""Give 20 subtopics for the topic {topic} to prepare for NEET exam for a beginner.

  """ + """return the output as python. Format:
        List[{"subtopic": subtopic1}]"""

        response = model.generate_content(prompt)
        print(response.text)
        return json.loads(filter_response(response.text))
    except Exception as e:
        return []


def get_prompt(subtopic, topic):
    return f"""
    create 2 simple questions belongs to the topic '{topic} - {subtopic}' to prepare for NEET exam.

    Task: Create a simple question similar to the above question with 4 options. The question description should be simple and easy for the students to answer.
    Also provide reasoning and detailed solution.

    """ + """
      Output:
      give python array
      [
        {
            "question": question_description,
            "options": [option1, option2, option3, option4],
            "correct_option": ("A" or "B" or "C" or "D"),
            "reasoning": reasoning
        }
      ]
  give python output
  """


def get_simple_question(subtopic, topic, solution):
    try:
        prompt = get_prompt(subtopic, topic)
        response = model.generate_content(prompt)

        solution.append(response.text)
        # print(response.text)
        print(subtopic)
    except ResourceExhausted as e:
        print(e)
        return get_simple_question(subtopic, topic)
    except Exception as e:
        print(e)


api_key = os.environ.get("GEMINI_API_KEY")
configure_client(api_key)

model = generativeai.GenerativeModel(
    model_name="models/gemini-1.0-pro"
)


def split_into_batches(array, batch_size=5):
    return [array[i:i + batch_size] for i in range(0, len(array), batch_size)]


for number in range(1, 166):
    input_file_path = f"""/home/barath/Documents/Neet/{number}.json"""
    output_file_path = f"""/home/barath/Documents/NeetSimple/{number}.json"""
    solution = []
    with open(input_file_path, 'r') as f:
        quiz = json.load(f)
        subtopics = get_subtopics(quiz["topic"])
        subtopic_batches = split_into_batches(subtopics, 20)
        print(subtopic_batches)
        for subtopic_batch in subtopic_batches:
            threads = []
            for subtopic in subtopic_batch:
                thread = threading.Thread(target=get_simple_question, args=(subtopic["subtopic"], quiz["topic"], solution))
                threads.append(thread)
                thread.start()
            for thread in threads:
                thread.join()

    with open(output_file_path, "w") as f:
        json.dump(solution, f, indent=4)
