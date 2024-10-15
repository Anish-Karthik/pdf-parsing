

import json
import markdown

input_file_path = f"""/home/barath/Documents/sat/code/pdf-parsing/gemini/Neet/53_material.json"""
solution = {}
output_file_path = f"""/home/barath/Documents/sat/code/pdf-parsing/gemini/Neet/53_material_output.json"""

output = ""
with open(input_file_path, 'r') as f:
    quiz = json.load(f)
    for question in quiz["questions"]:
        if "reading_material" in question and question["reading_material"] is not None:
            output += (markdown.markdown(question["reading_material"]) + "§")


output = output.replace("\n", "</br>")
with open(output_file_path, "w") as f:
    json.dump(output, f, indent=4)
