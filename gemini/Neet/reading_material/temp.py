import markdown

path = "/Users/pranav/GitHub/pdf-parsing/gemini/Neet/reading_material/51.1.md"

with open(path, "r") as f:
  text = f.read()

text = text.replace("\\n", "\n")
html = markdown.markdown(text)

with open("/Users/pranav/GitHub/pdf-parsing/gemini/Neet/reading_material/51.1.html", "w") as f:
  f.write(html)