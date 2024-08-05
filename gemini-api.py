import os
import google.generativeai as generativeai
from model import *
from prompt import *


def configure_client(api_key):
    generativeai.configure(
        api_key=api_key
    )


def get_writing_comprehension():

    raw_response = model.generate_content(
        prompt
    )
    # response = json.loads(raw_response.text)
    with open("raw_response.txt", "w") as f:
        f.write(raw_response.text)

    return raw_response.text

    # print(json.dumps(response, indent=4))


if __name__ == "__main__":
    api_key = os.environ.get("GEMINI_API_KEY")  # Replace with your actual API key
    configure_client(api_key)

    model = generativeai.GenerativeModel(
        model_name="models/gemini-1.5-pro-latest"
    )

    text = get_writing_comprehension()
