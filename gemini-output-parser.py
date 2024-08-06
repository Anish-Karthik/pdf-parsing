import glob
import re
import json


def remove_double_quotes(text):
    return re.sub(r"\"", "", i)


for ind, file_name in enumerate(glob.glob('output/gemini/*.txt')):
    json_list = []
    with open(file_name, 'r') as f:
        data = f.read()
        extracted_list = re.findall(r"\".*?(?<!\\)\"", data)

        blocks = []
        for i in extracted_list:
            blocks.append(remove_double_quotes(i))
            
            if len(remove_double_quotes(i)) <= 2:
                json_dict = {
                    "question" : blocks[0],
                    "options" : blocks[1:len(blocks)-1],
                    "correct_option" : blocks[-1]
                }
                json_list.append(json_dict)
                blocks = []

        json.dump(json_list, open(f"output/gemini-json/writing_comprehension_question_{ind}.json", 'w'), indent=4)
                
