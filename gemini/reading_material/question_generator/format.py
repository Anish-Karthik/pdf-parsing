import json
import os
import threading
import google.generativeai as generativeai
from pathlib import Path

directory_path = "/home/barath/Documents/qgen/questions/generated/"
formatted_path = "/home/barath/Documents/qgen/questions/formatted/"
output_path = "/home/barath/Documents/qgen/questions/formatted/"


def loop_through_files():
    files = []
    for filename in os.listdir(formatted_path):
        file_path = os.path.join(formatted_path, filename)
        if os.path.isfile(file_path):
            files.append(file_path)
    return files


def read_file(file_path):
    with open(file_path, 'r') as f:
        return f.read()


def get_filename_from_path(path):
    filename_with_ext = os.path.basename(path)
    filename, _ = os.path.splitext(filename_with_ext)
    return filename


def get_model():
    api_key = os.environ.get("GEMINI_API_KEY")
    generativeai.configure(api_key=api_key)

    return generativeai.GenerativeModel(model_name="models/gemini-1.5-flash")


model = get_model()


def convert_to_json(file_path):
    print(file_path)
    text = read_file(file_path)
    prompt = f"""{text}
    Merge the above into a single json.
    output: [
        description: question,
        options: [],
        answer: [a, b, c, d]
    ]
    """
    json_response = model.generate_content([prompt])
    output = json_response.text
    output = output.replace("```json", "")
    index = output.find("```")
    if index != -1:
        output = output[:index]

    output_file = "../questions/formatted/" + get_filename_from_path(file_path) + ".json"

    with open(output_file, 'w') as output_json:
        output_json.write(output)


def split_into_batches(array, batch_size):
    batches = []
    for i in range(0, len(array), batch_size):
        batch = array[i:i + batch_size]
        batches.append(batch)
    return batches


def format_content():
    files = loop_through_files()
    error_files = []
    file_batches = split_into_batches(files, 10)

    for batch in file_batches:
        threads = []
        for file_path in batch:
            try:
                t = threading.Thread(target=convert_to_json, args=(file_path,))
                threads.append(t)
                t.start()
            except BaseException:
                error_files.append(file_path)

        for thread in threads:
            thread.join()

    error_files.sort()

    for file in error_files:
        print(file)


def count_word_occurrences(filename, word):
    count = 0
    with open(filename, 'r') as file:
        content = file.read()
        return len(content.split(word))


def verify_formatting():
    total = 0
    errors = 0
    files = loop_through_files()
    for file in files:
        content = read_file(file)
        questions = json.loads(content)

        total += len(questions)
        for question in questions:
            is_error = False
            if "description" not in question:
                is_error = True
            options = question["options"]
            if len(options) != 4:
                is_error = True
            if "answer" not in question:
                is_error = True

            if is_error:
                errors += 1
                print(file)
                print(question)

    print(total)
    print(errors)
    print(total - errors)


verify_formatting()
