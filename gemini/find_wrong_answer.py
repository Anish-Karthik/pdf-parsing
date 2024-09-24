import os
import json


def get_sub(dir_list):
    files = []
    sub_dir = []
    for i in dir_list:
        if os.path.isdir(os.path.join(directory_path, i)):
            sub_dir.append(i)
        else:
            files.append(i)
    return files, sub_dir


def get_new_directory_path(directory_path, new_dir_name):
    index = directory_path.index("/", directory_path.index("/") + 1)
    new_directory_path = directory_path[:index] + "/" + new_dir_name + "/" + directory_path[index + 1:]
    return new_directory_path


def write_json(json_obj, file_name, new_directory_path):
    if os.path.exists(new_directory_path):
        pass
    else:
        os.mkdir(new_directory_path)
    with open(os.path.join(new_directory_path, file_name), "w") as f:
        json.dump(json_obj,f,indent=4)


def seperate_json(file, directory_path):
    json_obj = json.load(open(os.path.join(directory_path, file)))
    new_json_obj = json_obj.copy()
    
    questions = []
    for question in json_obj["questions"]:
      reasoning: str = question["reasoning"]
      if reasoning is not None and "closest option" in reasoning:
        questions.append(question)

    new_json_obj["questions"] = questions
      
    write_json(new_json_obj, file, get_new_directory_path(directory_path,  "for_review"))


def validate_files(files, directory_path):
    for file in files:
        if file[-5:] != ".json":
            print(f"Wrong format: {file} in {directory_path}")
        else:
            seperate_json(file, directory_path)


def recur_dir(directory_path):
    dir_list = sorted(os.listdir(directory_path))
    files, sub_dir = get_sub(dir_list)

    validate_files(files, directory_path)

    for dir in sub_dir:
        recur_dir(os.path.join(directory_path, dir))


directory_path = "gemini/gemini_output/sbi"
recur_dir(directory_path)
