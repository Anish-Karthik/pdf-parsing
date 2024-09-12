from gemini_api import *
import re
import time
from google.api_core.exceptions import ResourceExhausted
import json

def get_quiz_prompt():
    return """
    give 5 sample english quiz questions with options and correct option
    Output: give python dict("questions" : [{"question":question_description,
    "options": [option1,option2,option3,option4],
    "correct_option":("A" or "B" or "C" or "D")]
    })
    """

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
    # Regular expression pattern to match the code block
    pattern = r"```python"
    # Replace the code block with the replacement string
    replaced_text = re.sub(pattern, '', text, flags=re.DOTALL)
    pattern = r"```"
    replaced_text = re.sub(pattern, '', text, flags=re.DOTALL)
    return replaced_text
api_key = "AIzaSyBf8XSKPjDG5R640Y1P-CYNFOlZXfE83ws"
configure_client(api_key)

model = generativeai.GenerativeModel(
    model_name="models/gemini-1.5-flash"
)

raw_response = model.generate_content(
    get_quiz_prompt()
)
print(raw_response.text)
filtered_text = filter_response(raw_response.text)
structured_data = filtered_text.replace("python", "")
print(structured_data)
json_data = json.dumps(structured_data, indent=2)
# Save the JSON data to a file if it's not empty
if json_data:
    with open("/Users/muthupandi/Desktop/GitHub/pdf-parsing/gemini/output/gemini/raw_response.json", "w") as f:
        json.dump(json_data, f, indent=2)
else:
    print("No valid JSON data to save.")
