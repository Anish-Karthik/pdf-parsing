import os
import json
import re


def read_json(filename):
    with open(filename) as f:
        return json.load(f)


def write_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)


def fix_description(description):
    initial_match = re.search(r"difficulty", description)
    pattern = r"\*\*difficulty_level\*\*: (easy|Medium|hard|[5-9])"
    match = re.search(pattern, description)
    if match:
        # print(description)
        # print(str(question["id"]) + " " + match.group())
        # print("\n\n")
        question["description"] = re.sub(pattern, "", description, count=1)
        if match.group() not in difficulties:
            difficulties.append(match.group())
    elif initial_match:
        print(description)
        print(str(question["id"]))


def check_data(filename, difficulties):
    # print(filename)
    data = read_json(filename)

    for question in data['questions']:
        description = question["description"]
        initial_match = re.search(r"Difficulty", description)
        pattern = r"Difficulty.*10\)?"
        match = re.search(pattern, description)
        if match:
            start_index = match.start()
            # print(description)
            print(str(question["id"]) + " " + match.group())
            print("\n\n")

            # question["description"] = re.sub(pattern, "", description)
            # question["description"] = question["description"][:start_index]
        elif initial_match:
            print(description)
            print(str(question["id"]))

    write_json(data, filename)


def find_json_files(directory, difficulties):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".json"):
                check_data(os.path.join(root, file), difficulties)


# Example usage:
difficulties = []
directory_path = "/home/barath/Documents/Banking/"
json_files = find_json_files(directory_path, difficulties)
for difficulty in difficulties:
    print(difficulty)
