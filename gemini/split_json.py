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
title = "Para Jumbles"

json_path_list = sorted([f for f in os.listdir("gemini/output/para_jumbles") if f.endswith(".json")])

print(json_path_list)

for json_path in json_path_list:
  with open(f'gemini/output/para_jumbles/{json_path}', 'r') as json_file:
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
    sbi["title"] = title
    sbi["order"] = para_jumbles_topics.index(json_path[:-5]) + 1 + 14

    ibps = data.copy()
    ibps["questions"] = ibps_questions
    ibps["exam_id"] = ibps_exam_id
    ibps["title"] = title
    ibps["order"] = para_jumbles_topics.index(json_path[:-5]) + 1 + 14

    with open(f'gemini/output/sbi/para_jumbles/{json_path}', 'w') as json_file:
      json.dump(sbi, json_file, indent=4)

    with open(f'gemini/output/ibps/para_jumbles/{json_path}', 'w') as json_file:
      json.dump(ibps, json_file, indent=4)