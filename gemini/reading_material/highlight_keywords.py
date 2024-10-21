from gemini_utilities import *
from reading_material import get_correct_option
import threading

def get_highlighted_html(question):

    prompt = f"""
    question: {question["description"]}
    answer: {get_correct_option(question)}
    keywords: {question["keywords"]}
    
    wrap *unique* important data and keywords in the given html in a *span class="important"*
    length of each important keyword should be less than 3 words and 

    html:

    {question["content_html"]}
    """
    question["html_with_keywords"] = model.generate_content(
        prompt
    ).text

    question["html_with_keywords"] = question["html_with_keywords"].replace("```html\n", "")
    question["html_with_keywords"] = question["html_with_keywords"].replace("\n```", "")
    question["html_with_keywords"] = question["html_with_keywords"].replace("\n", "")
    question["html_with_keywords"] = question["html_with_keywords"].replace("\\\"", r"\"")



def highlight_keywords(path):

  with open(path, "r") as f:
      quiz = json.load(f)

      for question_batch in split_into_batches(quiz["questions"], 10):
        threads = []
        for question in question_batch:
            thread = threading.Thread(target=get_highlighted_html, args=(question,))
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()  

        with open(path, "w") as f:
            json.dump(quiz, f, indent=4)

highlight_keywords()
