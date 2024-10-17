from gemini_utilities import *


neet_pdf = upload_file_to_gemini("/Users/pranav/GitHub/pdf-parsing/gemini/Neet/ncert_books/biology/kebo120.pdf")
modules_raw = get_response_delayed_prompt(["Split the chapter from the pdf into smaller modules so that i can study with better understanding, give all the module headings", neet_pdf])
modules = change_response_to_list(modules_raw)
print(modules)


contents = []
for module in modules[1:2]:

  print(module)
  prompt = f"""help me learn this {module}, keep me engaged so that i understand, prepare a content about {module} using the above pdf so that i will be able to learn it later"""
  content = get_response_delayed_prompt([prompt, neet_pdf])

  prompt = f"""Give all the important words and keywords from the content"""
  keywords_raw = get_response_delayed_prompt(prompt+content)
  keywords = change_response_to_list(keywords_raw)
  
  print(keywords)
  print(content)