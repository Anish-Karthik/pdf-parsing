from gemini_utilities import *
import threading

def get_highlighted_html(page):
    prompt = f"""
    
    wrap 10 important data and keywords in the given html in a *span class="important"*
    length of each important keyword should be less than 3 words

    html:

    {page["content_html"]}
    """
    page["html_with_keywords"] = model.generate_content(
        prompt
    ).text

    page["html_with_keywords"] = page["html_with_keywords"].replace("```html\n", "")
    page["html_with_keywords"] = page["html_with_keywords"].replace("\n```", "")
    page["html_with_keywords"] = page["html_with_keywords"].replace("\n", "")
    page["html_with_keywords"] = page["html_with_keywords"].replace("\\\"", r"\"")

    output_json.append(page)

output_json = []
def highlight_keywords():
  path = "/Users/pranav/GitHub/pdf-parsing/gemini/Neet/reading_material/53_reading_material.json"
  global output_json

  with open(path, "r") as f:
      reading_material = json.load(f)

      for material_batch in split_into_batches(reading_material, 10):
        threads = []
        for page in material_batch:
            thread = threading.Thread(target=get_highlighted_html, args=(page,))
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()  

      with open(path, "w") as f:
          json.dump(output_json, f, indent=4)
          output_json = []
highlight_keywords()
# path = "/Users/pranav/GitHub/pdf-parsing/gemini/Neet/reading_material/51_reading_material.json"
# json_obj = read_json_file(path)

# for item in json_obj:
#   item["keyword_array"] = item["keywords"]
#   item["keywords"] = ", ".join(item["keyword_array"])

# write_json_file(path, json_obj)