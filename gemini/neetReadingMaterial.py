

import json
import markdown

input_file_path = f"""/home/barath/Documents/tamil/164-எட்டுத்தொகை, பத்துப்பாட்டு.json"""
solution = {}
output_file_path = f"""/home/barath/Documents/164-எட்டுத்தொகை, பத்துப்பாட்டு_output.json"""

output = ""
with open(input_file_path, 'r') as f:
    quiz = json.load(f)
    for question in quiz["questions"]:
        if "detailed_solution" in question and question["detailed_solution"] is not None:
            output += (markdown.markdown(question["detailed_solution"]) + "§")


output = output.replace("\n", "</br>")
with open(output_file_path, "w") as f:
    json.dump(output[1:len(output)], f, indent=4)
