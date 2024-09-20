import json
import os
math_topics = [
    "Number Systems",
    "Simplification and Approximation",
    "Data Interpretation",
    "Quadratic Equations",
    "Profit and Loss",
    "Simple Interest and Compound Interest",
    "Time and Work",
    "Time, Distance, and Speed",
    "Mensuration",
    "Average",
    "Ratio and Proportion",
    "Partnership",
    "Mixtures and Alligations",
    "Permutation and Combination",
    "Probability",
    "Data Sufficiency",
    "Inequalities",
    "Logarithms",
    "Surds and Indices",
    "Coordinate Geometry",
    "Trigonometry",
    "Algebra",
    "Geometry",
    "Calculus"
]

sbi_exam_id = 18
ibps_exam_id = 10
title = "Quantitative Ability"

json_path_list = sorted([f for f in os.listdir("gemini/output") if f.endswith(".json")])

print(json_path_list)

for json_path in json_path_list:
  with open(f'gemini/output/{json_path}', 'r') as json_file:
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
    sbi["order"] = math_topics.index(json_path[:-5]) + 1

    ibps = data.copy()
    ibps["questions"] = ibps_questions
    ibps["exam_id"] = ibps_exam_id
    ibps["title"] = title
    ibps["order"] = math_topics.index(json_path[:-5]) + 1

    with open(f'gemini/output/sbi/{json_path}', 'w') as json_file:
      json.dump(sbi, json_file, indent=4)

    with open(f'gemini/output/ibps/{json_path}', 'w') as json_file:
      json.dump(ibps, json_file, indent=4)