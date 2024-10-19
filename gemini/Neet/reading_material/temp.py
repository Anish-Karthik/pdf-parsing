import markdown
import json

path = "/Users/pranav/GitHub/pdf-parsing/gemini/Neet/reading_material/53_reading_material.json"
html_path = "/Users/pranav/GitHub/pdf-parsing/gemini/Neet/reading_material/html/"


with open(path, "r") as f:
  json_obj = json.load(f)

  
  for i,item in enumerate(json_obj):
    text = item["content"]
    html = markdown.markdown(text)

    item["content_html"] = html
    
    with open(html_path + str(i) + ".html", "w") as f:
      f.write(html)
