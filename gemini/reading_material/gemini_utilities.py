import google.generativeai as generativeai
import os
import re
import time
from google.api_core.exceptions import ResourceExhausted
import json
import traceback
import fitz
import threading



def clean_split(string : str, delimiter):
    li = string.split(delimiter)
    for i in li:
        if i == "":
            del i
    return li

def read_txt_file(file_path):
    with open(file_path, "r") as f:
        return f.read()

def write_txt_file(file_path, text):
    with open(file_path, "w") as f:
        f.write(text)

def get_python_code_from_response(response):
    return response[response.find("```python")+9:response.rfind("```")]

def configure_client(api_key):
    generativeai.configure(
        api_key=api_key
    )


def get_response_delayed_prompt(prompt, delay=0.1):
    try:
        time.sleep(delay)
        raw_response = model.generate_content(
            prompt
        )
        return raw_response.text
    except ResourceExhausted as e:
        print(traceback.format_exc())
        return get_response_delayed_prompt(prompt, delay * 2)
    except Exception as e:
        print(traceback.format_exc())
        return None


def get_html_from_response(raw_response):
    html = raw_response.replace("```html\n", "")
    endIndex = html.find("\n```")
    html = html[:endIndex]
    html = html.replace("\n", "")
    html = html.replace("\\\"", r"\"")

    return html

def change_response_to_list(raw_response) -> list:
    prompt_2 = f"""Convert the following raw response into a valid Python list.
    remove all unecessary characters:\n{raw_response}"""
    prompt_2_response = get_response_delayed_prompt(prompt_2)

    try:
        list_response = json.loads(filter_response_as_list(prompt_2_response))
        return list_response
    except Exception as e:
        print(traceback.format_exc())
        return prompt_2_response.split(",")


def read_json_file(file_path):
    with open(file_path, "r") as f:
        return json.load(f)


def call_collection_with_threading(func=None, args=(), threads=10, collection=None):
    for item_batch in split_into_batches(collection, 10):
        threads = []
        for item in item_batch:
            thread = threading.Thread(target=func, args=(item, *args))
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()


def write_json_file(file_path, data):
    with open(file_path, "w") as f:
        f.write(data)


def filter_response(text):
    text = re.sub("\\*{2,}", "", text)
    text = text[text.index("{"):text.rindex("}") + 1]
    return text


def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    pdf_text = ""
    for page in doc:
        pdf_path += page.get_text("text") + "\n"


def filter_response_as_list(text):
    # text = re.sub("\\*{2,}", "", text)
    return text[text.index("["):text.rindex("]") + 1]


def upload_file_to_gemini(file):
    print("uploading...")
    upload_file = generativeai.upload_file(file)
    print("file uploaded successfull!")
    return upload_file


def split_into_batches(array, batch_size=5):
    return [array[i:i + batch_size] for i in range(0, len(array), batch_size)]


api_key = os.getenv("GEMINI_API_KEY")
configure_client(api_key)

model = generativeai.GenerativeModel(
    model_name="gemini-1.5-flash"
)
