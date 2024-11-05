
import json


def read_json(filename):
    with open(filename) as f:
        return json.load(f)


questions_array = read_json("/home/barath/Documents/Neet/questions.json")
print(len(questions_array))
for questions in questions_array:
    # print(len(questions_array))
    for question in questions:
        if "detailed_solution" not in question:
            continue
        detailed_solution = question["detailed_solution"]
        # print(question["id"])

        if "Unfortunately" in detailed_solution:
            print(question["id"])
