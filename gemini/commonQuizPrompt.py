from gemini_api import *
import re
import pandas as pd
import time
from google.api_core.exceptions import ResourceExhausted

def get_quiz_prompt():
  return f"""
    give 5 sample english quiz questions with options and correct option
    Output: give python list(question,[option1,option2,option3,option4],correct_option("A" or "B" or "C" or "D"))
    """

def get_quiz_delayed_prompt(delay=15):
  try:
    time.sleep(delay)
    raw_response = model.generate_content(
      get_quiz_prompt()
    )
    # print(raw_response.text)
    return filter_response(raw_response.text)
  except ResourceExhausted as e:
    print("delay:",delay,e)
    return get_quiz_delayed_prompt(delay*2)

def filter_response(text):
  return re.sub("\*{1,2}","",text)




api_key = os.environ.get("GEMINI_API_KEY")
configure_client(api_key)

model = generativeai.GenerativeModel(
    model_name="models/gemini-1.5-flash"
)

raw_response = model.generate_content(
  get_quiz_prompt()
)
with open("output/gemini/raw_response.txt", "w") as f:
    f.write(raw_response.text)


  

