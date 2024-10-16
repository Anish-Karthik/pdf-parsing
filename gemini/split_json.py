import json
import os
para_jumbles_topics = [
    "Paragraph coherence: Understanding the overall theme and flow of the paragraph",
    "Logical sequencing: Identifying the correct order of sentences based on cause-and-effect relationships, chronological order, or thematic progression",
    "Topic sentences: Identifying the main idea of the paragraph",
    "Supporting details: Understanding how supporting sentences relate to the topic sentence",
    "Conjunctions and transition words: Recognizing the role of connectors in establishing relationships between sentences",
    "Contextual clues: Using hints and clues within the paragraph to determine the correct sequence",
    "Sentence structure and grammar: Understanding how sentence structure and grammar affect the overall coherence and flow"
]

ibps_exam_id = 9
sbi_exam_id = 16
copy_from = "gemini/gemini_output/new/sbi/fill_ups/"
copy_to = "gemini/gemini_output/new/ibps/fill_ups/"
# title = "Logical Reasoning"

json_path_list = sorted([f for f in os.listdir(f"{copy_from}") if f.endswith(".json")])

print(json_path_list)

for json_path in json_path_list:
    with open(f'{copy_from}{json_path}', 'r') as json_file:
      data = json.load(json_file)

      sbi_questions = []
      ibps_questions = []

      for i,question in enumerate(data["questions"]):
        if i % 2 == 0:
          ibps_questions.append(question)
        else:
          sbi_questions.append(question)

      sbi = data.copy()
      sbi["questions"] = sbi_questions
      sbi["exam_id"] = sbi_exam_id

      ibps = data.copy()
      ibps["questions"] = ibps_questions
      ibps["exam_id"] = ibps_exam_id

      if not os.path.exists(f'{copy_from}'):
        os.mkdir(f'{copy_from}')
      with open(f'{copy_from}{json_path}', 'w') as json_file:
        json.dump(sbi, json_file, indent=4)

      if not os.path.exists(f'{copy_to}'):
        os.mkdir(f'{copy_to}')
      with open(f'{copy_to}{json_path}', 'w') as json_file:
        json.dump(ibps, json_file, indent=4)