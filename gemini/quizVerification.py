from commonQuizPrompt import *


def verify_questions(question):

  option_map = {
    "A": 0,
    "B": 1,
    "C": 2,
    "D": 3
  }

  correct_option = question["options"][option_map[question["correct_option"]]]
  
  question["valid"] = get_response_delayed_prompt(
    f"""
    <question>
    {question["question"]}
    </question>

    <answer>
    {correct_option}
    </answer>

    1.verify if the question is phrased correctly without any grammatical errors
    2.fill the blank with the answer given above and verify if the answer is correct also verify that the entire sentence is phrased correctly without any grammatical errors


    if everything is correct return true, otherwise return false
    Output:
    {{
      "valid": true or false
    }}
    """
  )

dir_path = "gemini_output/new/ibps/fill_ups/"
dir_list = os.listdir(dir_path)
for file in dir_list:
  print(file)
  # json_path = "gemini_output/new/ibps/fill_ups/Fill ups - Articles: A, an, the.json"
  with open(dir_path+file,"r") as f:
    data = json.load(f)
    questions = data["questions"]

    question_batches = split_into_batches(questions,10)
    for question_batch in question_batches:
      threads = []
      for question in question_batch:
        thread = threading.Thread(target=verify_questions, args=(question,))
        threads.append(thread)
        thread.start()
      for thread in threads:
        thread.join()
  data["questions"] = questions

  with open(dir_path+file,"w") as f:
    json.dump(data,f,indent=2)  
      