from commonQuizPrompt import *
import os

def get_detailed(json):
  return get_response_delayed_prompt(
    f"""
    <question>
      {json["question"]}
      {json["options"]}
      <correct option>
        {json["correct_option"]}
      </correct option>
    </question>
    **Role**
      Teacher

    **Task**
      Tell the correct option based on the given correct option
      Understand the question clearly, 
      Solve the above problem step by step and give a detailed and comprehensive solution for why the given correct option is correct
      The content should be useful for a student to learn and apply the same content for answering similar questions.
    """
  )

def convert_detailed_to_json(response):
  return get_response_delayed_prompt(
    f"""
    Convert the following text to a valid JSON format:
    <detailed_answer>
      {response}
    </detailed_answer>

    **Output**
      {{
        "detailed_answer": "detailed explanation of the answer"
      }}
    """
  )

def is_standalone(json):
  return get_response_delayed_prompt(
    f"""
    <question>
      {json["question"]}
      {json["options"]}
      {json["correct_option"]}
    </question>

    **Task**
      Determine if we can answer the above question with the given data and tell if it is sufficient or not,
      Give true if it is sufficient and false if it is not sufficient

    **Output**
      give valid json
      {{
        "standalone": true | false
      }}
    """
  )

def classify_topic(json):
  return get_response_delayed_prompt(
    f"""
    <question>
      {json}
    </question>

    **Task**
      Classify the topic of the above question into one of the following:
        1. English Language
        2. Quantitative Aptitude
        3. Reasoning

    **Output**
      give valid json
      {{
        "topic": "English Language" | "Quantitative Aptitude" | "Reasoning"
      }}
    """
  )

def get_new_json(json_file):
  with open(path+json_file) as f:
    jsons = json.load(f)
    new_jsons = []

    for data in jsons:
      data["standalone"] = is_standalone(data) 
      data["topic"] = classify_topic(data["question"])
      data["reasoning"] = get_detailed(data)

      try:
        data["topic"] = json.loads(data["topic"][data["topic"].find("{"):data["topic"].find("}")+1])["topic"]
      except Exception as e:
        print(e)

      try:
        data["standalone"] = json.loads(data["standalone"][data["standalone"].find("{"):data["standalone"].find("}")+1])["standalone"]
      except Exception as e:
        print(e)

      print(data)
      new_jsons.append(data)

    with open(path+json_file, 'w') as f:
      json.dump(new_jsons, f, indent=4)

path = "/Users/pranav/GitHub/pdf-parsing/Bank_exam_parsing/parsing-output/"
json_files = sorted(os.listdir(path))

threads = []
# for json_file in json_files:
for json_file in ["IBPS PO 2020 Questions 1.json","IBPS PO Prelims QP 2023.json"]:
  # get_new_json(json_file)
  thread = threading.Thread(target=get_new_json, args=(json_file,))
  threads.append(thread)
  thread.start()
for thread in threads:
  thread.join()

    
    
    
    