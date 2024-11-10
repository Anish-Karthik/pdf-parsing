import json
import os
import threading
import google.generativeai as generativeai
import re
import ast

formatted_path = "/home/barath/Documents/qgen/questions/formatted/"
output_path = "/home/barath/Documents/qgen/questions/processed/"


def get_model():
    api_key = os.environ.get("GEMINI_API_KEY")
    generativeai.configure(api_key=api_key)

    return generativeai.GenerativeModel(model_name="models/gemini-1.5-flash")


model = get_model()


def file_exists(file_path):
    return os.path.isfile(file_path)


def get_filename_from_path(path):
    filename_with_ext = os.path.basename(path)
    filename, _ = os.path.splitext(filename_with_ext)
    return filename


def loop_through_files():
    files = []
    for filename in os.listdir(output_path):
        file_path = os.path.join(output_path, filename)
        if os.path.isfile(file_path):
            files.append(file_path)
    return files


def split_string(string):
    match = re.search(r"(.+?(\d+-\d+))", string)
    if match:
        return match.group(1)
    else:
        return None


def is_valid_json(json_str):
    try:
        json.loads(json_str)
        return True
    except json.JSONDecodeError:
        return False


def read_file(file_path):
    with open(file_path, 'r') as f:
        return f.read()


def split_into_batches(array, batch_size):
    batches = []
    for i in range(0, len(array), batch_size):
        batch = array[i:i + batch_size]
        batches.append(batch)
    return batches


def process_questions(questions, output_file, uploaded_file, retry=2):
    output_path = f"../questions/processed/{output_file}.json"
    if file_exists(output_path):
        # print(f"Already processed {output_file}")
        return

    print(f"processing {output_file}")

    prompt = f"""{questions}
  Add additional context and details related to each question from the pdf provided.
  The context should be detailed and easy to read for a student.
  Context should be in tamil and should at least be of 100 words.

  output: [
      description: question,
      options: [],
      answer: [a, b, c, d],
      additional_context: additional_context
  ]
  """
    json_response = model.generate_content([prompt, uploaded_file])
    output = json_response.text
    # print(output)
    output = output.replace("```json", "")
    index = output.find("```")
    if index != -1:
        output = output[:index]

    if not is_valid_json(output):
        if retry != 0:
            process_questions(questions, output_file, uploaded_file, retry - 1)
        else:
            return

    output_path = f"../questions/processed/{output_file}.json"

    with open(output_path, 'w') as output_json:
        output_json.write(output)


def format_content():
    files = loop_through_files()

    for index, file in enumerate(files):
        print(len(files) - index)
        print(file)
        questions = json.loads(read_file(file))
        question_batches = split_into_batches(questions, 5)

        processed = True
        for index, batch in enumerate(question_batches):
            output_file = f"{get_filename_from_path(file)}-{index}"
            output_path = f"../questions/processed/{output_file}.json"
            if not file_exists(output_path):
                processed = False

        if processed:
            continue

        pdf_name = f"../generated/{split_string(get_filename_from_path(file))}.pdf"
        uploaded_file = generativeai.upload_file(pdf_name)

        threads = []
        for index, batch in enumerate(question_batches):
            output_file = f"{get_filename_from_path(file)}-{index}"
            t = threading.Thread(target=process_questions, args=(batch, output_file, uploaded_file,))
            threads.append(t)
            t.start()
        for thread in threads:
            thread.join()


def convert_to_json(content):
    prompt = f"""{content}
    Fix the above content into a valid json. Make sure that the json is valid.
    """
    json_response = model.generate_content([prompt])
    output = json_response.text
    output = output.replace("```json", "")
    index = output.find("```")
    if index != -1:
        output = output[:index]

    return output


def fix_content(data):
    questions = data.split("[", 1)[1].rsplit("]", 1)[0].split("},")
    close_bracket = "}"
    question_strs = []
    for question in questions:
        desciption = question.split("\"options\"")[0].split("\"description\": ")[1].strip()
        context = question.rsplit("\n  }")[0].split("\"additional_context\": ")[1].strip()

        desciption = desciption.replace("\"", "'")
        desciption = desciption.replace("\\\'", "'")
        if desciption[0] == "'":
            desciption = "\"" + desciption[1:]

        if desciption[len(desciption) - 2] == "'":
            desciption = desciption[:-2] + "\","

        # print("$$" + context + "$$")
        context = context.replace("\"", "'")
        context = context.replace("\\\'", "'")
        if context[0] == "'":
            context = "\"" + context[1:]

        if context[len(context) - 1] == "'":
            context = context[:-1] + "\""

        # print(desciption)
        # print(context)
        part1 = question.split("\"description\": ")[0]
        part2 = question.split("\"options\": ")[1].split("\"additional_context\": ")[0]
        question_str = f"""
          {part1}
          "description": {desciption}
          "options": {part2}
          "additional_context": {context}
          {close_bracket}
        """

        question_strs.append(question_str)

    # print("[" + ",".join(question_strs) + "]")
    return "[" + ",".join(question_strs) + "]"


def get_context_count():
    files = loop_through_files()
    count = 0
    error_count = 0
    files.sort()
    for index, file in enumerate(files):
        try:
            content = read_file(file)
            try:
                questions = json.loads(content)
            except BaseException:
                output = fix_content(content)
                if is_valid_json(output):
                    with open(file, 'w') as output_json:
                        output_json.write(output)

                questions = json.loads(output)

            for question in questions:
                if "additional_context" in question:
                    count += 1
        except BaseException:
            print(file)
            os.remove(file)

    print(count)
    print(error_count)


get_context_count()
