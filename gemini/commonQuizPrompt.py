from gemini_api import *
from content import *
import re
import time
from google.api_core.exceptions import ResourceExhausted
import json


def get_theme(sample_questions) -> List[str]:
    themes = get_response_delayed_prompt(
        f"""
        Task:

        if you were to assign a theme for each question given in the sample questions, what would it be, the theme can be anything from where that question/topic might have been referenced from, create 50 different topics similar to the sample questions.

        Sample Questions:
        {sample_questions}
        """
    )

    themes_list = get_response_delayed_prompt(
        f""" {themes}

        get python list of themes from the given themes
        output format:
        python list["theme]
        """
    )

    return json.loads(filter_response(themes_list))

def get_question_prompt(sample_questions):
    return get_response_delayed_prompt(
        f""" Sample prompt:
        
        create two fill in the blanks question with multiple choice with atleast two lines objective type with its correct answer and provide reasoning for the correct answer and why other options are wrong. 
        verify everything is correct
            Example:     

        The direct message was that NATO would no longer __ Russian sensitivities on the subject of NATO expansion.
        1. Hinder 
        2. Alter 
        3. Deliquesce 
        4. Dissipate 
        5. Consider 

        Correct Option - 5

    Task:
    
    create a prompt to generate a sample question type questions
    the new prompt should be based on the sample prompt but the objective is to generate similar to sample questions.

    Sample question:
    {sample_questions}"""
    )

def get_quiz_json_prompt(question_prompt,theme,skills):
    return f"""
      {question_prompt}

      Topic:
      The questions should be based on:{theme} and test {skills}

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


def get_response_delayed_prompt(prompt,delay=15):
    try:
        time.sleep(delay)
        raw_response = model.generate_content(
            prompt
        )
        # print(raw_response.text)
        return raw_response.text
    except ResourceExhausted as e:
        print("delay:", delay, e)
        return get_response_delayed_prompt(prompt,delay * 2)
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

# sample_questions = input("Enter sample questions: ")
question_prompt = get_question_prompt(sample_questions)
themes = get_theme(sample_questions)
skills = get_response_delayed_prompt(f"""what skills does these sample questions test
    Sample Questions:
    {sample_questions}""")
print(question_prompt,themes,skills)

for theme in themes:
    json_text = filter_response(
            get_response_delayed_prompt(
                get_quiz_json_prompt(question_prompt,theme,skills)
            )
        )

    if json_text is None:
        continue

    try:
        qns_json = json.loads(json_text)
        for qn_json in qns_json:
            all_qns_json.append(qn_json)
            print(str(qn_json)+"\n\n\n")
    except Exception as e:
        print(e)
        
final_qns_json = []
for qn_obj in all_qns_json:
    final_qns_json.append({
        "question": qn_obj["question"],
        "options": qn_obj["options"],
        "correct_option": qn_obj["correct_option"],
        "detailed_solution": qn_obj["reasoning"]
    })
with open('output/final_test.json', 'w') as json_file:
    json.dump(final_qns_json, json_file, indent=4)

    
  
  

