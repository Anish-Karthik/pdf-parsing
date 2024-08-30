from gemini_api import *
import re
import pandas as pd
import time
from google.api_core.exceptions import ResourceExhausted

def get_tamil_prompt(qn, op1,op2,op3,op4, correct_option):
  return f"""
    question: {qn} 
    
    options: 
    [A:{op1},
    B:{op2},
    C:{op3},
    D:{op4}]
    
    answer: {correct_option}
    now give only the detailed explanation and reasoning in tamil, also state why other options are incorrect

    the output should be readable and simple to understand and avoid using * and ** for bold characters
    """

def get_tamil_detailed_solution(qn, op1,op2,op3,op4, correct_option,delay=15):
  try:
    time.sleep(delay)
    raw_response = model.generate_content(
      get_tamil_prompt(qn, op1,op2,op3,op4, correct_option)
    )
    # print(raw_response.text)
    return filter_response(raw_response.text)
  except ResourceExhausted as e:
    print("delay:",delay,e)
    return get_tamil_detailed_solution(qn, op1,op2,op3,op4, correct_option,delay*2)

def filter_response(text):
  return re.sub("\*{1,2}","",text)




api_key = os.environ.get("GEMINI_API_KEY")
configure_client(api_key)

model = generativeai.GenerativeModel(
    model_name="models/gemini-1.5-flash"
)

input_file_path = "input/gemini/Questions detail solution.xlsx"
output_file_path = "output/gemini/Questions AI detailed solution.xlsx"
df = pd.read_excel(input_file_path)
output_df = pd.read_excel(output_file_path)
for i, row in df.iterrows():
  if i < 63:
    continue

  row["Detailed_Answer"] = get_tamil_detailed_solution(
    row["Questions"],
    row["Option 1"],
    row["Option 2"],
    row["Option 3"],
    row["Option 4"],
    row["Answer"]
  )
  output_df = output_df._append(row, ignore_index=True)
  output_df.to_excel(output_file_path, index=False)
  print(i)
  

