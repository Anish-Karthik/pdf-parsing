from gemini_api import *
from content import *
import re
import time
from google.api_core.exceptions import ResourceExhausted
import json


def get_quiz_prompt(sample):
    return f"""
      Task:
  create fill in the blanks questions with options and its correct answer
  each questions should have a minimum of 20-30 words and the questions is of the type fill in the blanks

  Rules:
  Each question should be unique
  evenly spread the correct options
  EX. idioms and phrases, or test grammer knowledge
  The questions should be structured from real world examples or statements
  and options should be idioms
  Make the question and option more interesting for indian learners

  generate 10 fill in the blanks questions with options and its correct answer
      Output: give python dict("question":question_description
      ,"options": [option1,option2,option3,option4],
      "correct_option":("A" or "B" or "C" or "D")
      )

  sample:
  {sample}"""


def get_quiz_delayed_prompt(delay=15):
    try:
        time.sleep(delay)
        raw_response = model.generate_content(
            get_quiz_prompt()
        )
        return filter_response(raw_response.text)
    except ResourceExhausted as e:
        print("delay:", delay, e)
        return get_quiz_delayed_prompt(delay * 2)


def filter_response(text):
    text = re.sub("\*{2,}","",text)
    return text[text.index("["):text.rindex("]") + 1]
  
api_key = os.getenv("GEMINI_API_KEY")
configure_client(api_key)

model = generativeai.GenerativeModel(
    model_name="models/gemini-1.5-flash"
)

raw_response = model.generate_content(
      get_quiz_prompt(underline[0])
)
filtered_text = filter_response(raw_response.text)


if filtered_text:
    with open("gemini/output/raw_response.json", "w") as f:
        json.dump(json.loads(filtered_text), f, indent=2)
else:
    print("No valid JSON data to save.")
with open("output/gemini/raw_response.txt", "w") as f:
    f.write(raw_response.text)
