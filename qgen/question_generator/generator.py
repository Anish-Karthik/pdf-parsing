import csv
import json
import os
import threading
from pdf_util import extract_filename_without_extension, split_pdf
import google.generativeai as generativeai  # type: ignore

input_pdf_path = "/home/barath/Documents/qgen/10th_Tamil_optimised.pdf"
output_folder = "/home/barath/Documents/qgen/generated"
questions_folder = "/home/barath/Documents/qgen/questions"
csv_file = "/home/barath/Documents/qgen/extra tamil questions - 10th std .csv"
standard = "7"


def read_csv_as_list(filename):
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        data = list(reader)
    return data


def get_model():
    api_key = os.environ.get("GEMINI_API_KEY")
    generativeai.configure(api_key=api_key)

    return generativeai.GenerativeModel(model_name="models/gemini-1.5-flash")


def upload_file(file):
    file = generativeai.upload_file(file)

    prompt = f"""
            Read the attached pdf and return the content as it is.

            Format it better.

            **Don't omit any information.**

            Output should be in tamil language.
        """
    response = model.generate_content([prompt, file])
    print(response.text)
    return response.text


def get_questions(metadata, pdf_content, results):
    prompt = f"""
        {pdf_content}

        Generate MCQ questions with 4 options and the answers from the above content.

        Avoid stright forward questions. Make it as detailed as possible.

        **{metadata}**

        Verify that the questions are correctly phrased and the options are valid.

        The complete output should be in tamil.
    """

    response = model.generate_content(prompt)

    # print(response.text)

    prompt = f"""{response.text}
    Convert the above in the following json format. answer should be either A,B,C or D. verify this.
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

    print(output)

    results.append(output)


model = get_model()
data = read_csv_as_list(csv_file)
print(data)

for row in data:
    try:
        generated_file = split_pdf(input_pdf_path, output_folder, int(row[0]), int(row[1]))
        print(generated_file)

        pdf_content = upload_file(generated_file)
        threads = []
        results = []
        metadata = [
            "Questions should test the tamil meaning skills of the student",
            f"Questions should test the skills from the topic {row[2]}",
            f"Mix multiple data points to generate questions to test the knowledge of the student.",
            "Give a portion of the input content from the above and ask a question related to the content.",
            "Generate questions in a way where the student has to read the entire content provided for answering the questions.",
            "Create fill ups based on the content provided and provide 4 options for the fill up option."]

        for i in range(len(metadata)):
            t = threading.Thread(target=get_questions, args=(metadata[i], pdf_content, results))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        input_file_name = extract_filename_without_extension(input_pdf_path)
        questions_file_name = f"{input_file_name}-{row[0]}-{row[1]}-{row[2]}.json"
        questions_file_path = os.path.join(questions_folder, questions_file_name)

        with open(questions_file_path, 'w') as output_json:
            output_json.write("".join(results))
    except BaseException:
        print(row)
