import json
json_path = "gemini/gemini_output/sbi/quant/Algebranew.json"
nums = 0

with open(json_path) as f:
  dataf = f.read()
  datajson = json.loads(dataf)
  
  for data in datajson["questions"]:
    # print(data["another_answer"])
    options_map = {
      "A": 0,
      "B": 1,
      "C": 2,
      "D": 3
    }
    try:
      another_answer = json.loads(data["another_answer"])
      if(str(another_answer["correct answer"]) != data["options"][options_map[data["correct_option"]]].strip() or True):
        nums+=1
        print(another_answer["correct answer"])
        print(data["options"][options_map[data["correct_option"]]])
        print(data["is_correct"])
        print("\n\n\n")
    except Exception as e:
      another_answer = data["another_answer"]
      nums+=1
      print(another_answer,data["options"][options_map[data["correct_option"]]])
      print(data["is_correct"])
      print("\n\n\n")

print(nums)

    # if(another_answer["correct_answer"] != data["options"][options_map[data["correct_option"]]]):
    #   print(another_answer["correct_answer"],data["options"][options_map[data["correct_option"]]])