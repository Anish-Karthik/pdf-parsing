import os
import google.generativeai as generativeai
from model import *
from prompt import *
import json
import glob

def configure_client(api_key):
    generativeai.configure(
        api_key=api_key
    )


def get_writing_comprehension(json_data, i):

    raw_response = model.generate_content(
        get_prompt(json_data["passage"])
    )
    
    with open(f"output/gemini/raw_response{i}.txt", "w") as f:
        f.write(raw_response.text)

    # print(json.dumps(response, indent=4))


if __name__ == "__main__":
    api_key = os.environ.get("GEMINI_API_KEY")  # Replace with your actual API key
    configure_client(api_key)

    model = generativeai.GenerativeModel(
        model_name="models/gemini-1.5-pro-latest"
    )

    # for i, json_data in enumerate(map(lambda x: json.load(x), map(open, glob.glob("input/gemini/*.json")))):
    #     get_writing_comprehension(json_data, i)
    for i in range(3,4):
        json_data = json.load(open(f"input/gemini/College Duniya SAT Sample Passage {6+i}.json"))
        get_writing_comprehension(json_data, i)
