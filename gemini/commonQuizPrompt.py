from gemini_api import *
from content import *
import re
import time
from google.api_core.exceptions import ResourceExhausted
import json


def get_quiz_prompt(text):
    return f"""
      {underlined_prompt}

      Topic:
      The questions should be based on:{text} and test their English skills not their general knowledge

    """+"""
      Output: 
      give python 
      [
            "question":question_description,
            "options":[option1,option2,option3,option4],
            "correct_option":("A" or "B" or "C" or "D"),
            "reasoning":reasoning
      ]
  give python output 
  """


def get_quiz_delayed_prompt(text,delay=15):
    try:
        time.sleep(delay)
        raw_response = model.generate_content(
            get_quiz_prompt(text)
        )
        # print(raw_response.text)
        return filter_response(raw_response.text)
    except ResourceExhausted as e:
        print("delay:", delay, e)
        return get_quiz_delayed_prompt(delay * 2)
    except Exception as e:
        print(e)
        return None


def filter_response(text):
    text = re.sub("\*{2,}","",text)
    return text[text.index("["):text.rindex("]") + 1]
  
api_key = os.getenv("GEMINI_API_KEY")
configure_client(api_key)

model = generativeai.GenerativeModel(
    model_name="gemini-1.5-flash"
)

all_qns_json = []

for theme in underlined_themes:
  json_text = get_quiz_delayed_prompt(theme)
  qns_json = json.loads(json_text)
  
  for qn_json in qns_json:
      all_qns_json.append(qn_json)

    
  
  

