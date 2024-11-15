from gemini_utilities import read_json_file, write_json_file
import re
import markdown
def clean_reading_material(path):
    quiz = read_json_file(path)

    for question in quiz["questions"]:
        if "html_with_keywords" not in question:
            continue
        html_with_keywords = question["html_with_keywords"]

        html_with_keywords = html_with_keywords.replace('style=\"color:red;\"', "")
        html_with_keywords = html_with_keywords.replace('style=\"color:red\"', "")
        html_with_keywords = html_with_keywords.replace('style=\"background-color:yellow\"', "")
        html_with_keywords = html_with_keywords.replace('style=\"background-color:yellow;\"', "")
        html_with_keywords = markdown.markdown(html_with_keywords)
        
        title_regex = r"<title>.*?</title>"
        html_with_keywords = re.sub(title_regex, "", html_with_keywords)

        question["html_with_keywords"] = html_with_keywords

    remove_empty_questions(quiz)
    write_json_file(path, quiz)

def remove_empty_questions(quiz):
    for question in quiz["questions"]:
        if "html_with_keywords" in question and len(question["html_with_keywords"].split()) < 100:
            del question["html_with_keywords"]

    # write_json_file(path, quiz)


clean_reading_material("/Users/pranav/GitHub/pdf-parsing/gemini/Neet/5.json")
clean_reading_material("/Users/pranav/GitHub/pdf-parsing/gemini/Neet/50.json") 
clean_reading_material("/Users/pranav/GitHub/pdf-parsing/gemini/Neet/51.json") 
clean_reading_material("/Users/pranav/GitHub/pdf-parsing/gemini/Neet/52.json") 
