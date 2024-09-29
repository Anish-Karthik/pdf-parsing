from commonQuizPrompt import *
import threading
import json
json_path = "gemini/gemini_output/sbi/quant/Algebranew.json"

with open(json_path) as json_file:
  data = json.load(json_file)
  option_map = {
      "A": 0,
      "B": 1,
      "C": 2,
      "D": 3
  }
  # threads = []
  for i in data['questions']:
  #   thread = threading.Thread(target=get_subtopic_question, args=(subtopic["subtopic"], difficulty, quiz_questions))
  #   threads.append(thread)
  #   thread.start()
  # for thread in threads:
  #   thread.join()

    correct_prompt = f"""
    <question>
    {i['question']}
    </question>

    solve this question step by step, and give the final answer as the output.
    Once you find the answer verify the final answer by reviewing each step.

    """+"""<output> json
      {
        "correct answer" : correct_answer
      }
    </output>
    """
    is_correct_prompt = f"""
    <question>
    {i['question']}
    </question>

    <correct_answer>
    {i['options'][option_map[i['correct_option']]]}
    </correct_answer>

   <task>
    is the given answer correct for the above question?
   </task>

    """+"""<output> json
      {
        "is_correct" : (true (or) false)
      }
    </output>
    """


    another_answer = get_response_delayed_prompt(is_correct_prompt)
    another_answer = another_answer[another_answer.index("{"):another_answer.rindex("}")+1]
    print(another_answer+"\n\n\n")
    i["is_correct"] = another_answer

new_json_path = "gemini/gemini_output/sbi/quant/Algebranew.json"
with open(new_json_path, 'w') as outfile:
    json.dump(data, outfile, indent=4)

