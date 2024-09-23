import os
import json

filename = 'Average.json'
optionPrefix = [['A. ', 'A) ', 'a) ', '(1) ', '(A)', 'A: ', 'a: ', '(a) '], ['B. ', 'B) ', 'b) ', '(2) ', '(B)', 'B: ', 'b: ', '(b) '], ['C. ', 'C) ', 'c) ', '(3) ', '(C)', 'C: ', 'c: ', '(c) '], ['D. ', 'D) ', 'd) ', '(4) ', '(D)', 'D: ', 'd: ', '(d) ']]

correct_opt = ['A', 'B', 'C', 'D']
small_correct_opt = ['a', 'b', 'c', 'd']

topics_list = topics = [
    "Quants - Number Systems",
    "Quants - Simplification and Approximation",
    "Quants - Data Interpretation",
    "Quants - Quadratic Equations",
    "Quants - Profit and Loss",
    "Quants - Simple Interest and Compound Interest",
    "Quants - Time and Work",
    "Quants - Time, Distance, and Speed",
    "Quants - Mensuration",
    "Quants - Average",
    "Quants - Ratio and Proportion",
    "Quants - Partnership",
    "Quants - Mixtures and Alligations",
    "Quants - Permutation and Combination",
    "Quants - Probability",
    "Quants - Data Sufficiency",
    "Quants - Inequalities",
    "Quants - Logarithms",
    "Quants - Surds and Indices",
    "Quants - Coordinate Geometry",
    "Quants - Trigonometry",
    "Quants - Algebra",
    "Quants - Geometry",
    "Quants - Calculus",
    "English - Multiple Meaning",
    "English - Error Spotting",
    "English - Paragraph Completion",
    "Fill ups - Tenses",
    "Fill ups - Modals",
    "Fill ups - Articles: A, an, the",
    "Fill ups - Prepositions",
    "Fill ups - Conjunctions",
    "Fill ups - Adjectives and adverbs",
    "Fill ups - Pronouns",
    "Fill ups - Subject-verb agreement",
    "Fill ups - Sentence structure",
    "Fill ups - Vocabulary: Synonyms and antonyms",
    "Fill ups - Vocabulary: Phrasal verbs",
    "Fill ups - Vocabulary: Idioms and proverbs",
    "Fill ups - Vocabulary: Collocations",
    "Fill ups - Vocabulary: One-word substitutes",
    "Para Jumble - Paragraph coherence",
    "Para Jumble - Logical sequencing",
    "Para Jumble - Topic sentences",
    "Para Jumble - Supporting details",
    "Para Jumble - Conjunctions and transition words",
    "Para Jumble - Contextual clues",
    "Para Jumble - Sentence structure and grammar",
    "Logical Reasoning - Alphanumeric Series",
    "Logical Reasoning - Ranking/Direction/Alphabet Test",
    "Logical Reasoning - Data Sufficiency",
    "Logical Reasoning - Coded Inequalities",
    "Logical Reasoning - Seating Arrangement",
    "Logical Reasoning - Puzzle",
    "Logical Reasoning - Syllogism",
    "Logical Reasoning - Clocks",
    "Logical Reasoning - Blood Relations",
    "Logical Reasoning - Input-Output",
    "Logical Reasoning - Coding-Decoding",
    "Logical Reasoning - Calendars",
    "Logical Reasoning - Dice",
    "Logical Reasoning - Cube and Cuboid",
    "Logical Reasoning - Truth Tables",
    "Logical Reasoning - Ranking-Direction-Alphabet Test",
    "Reading Comprehension"
]


def read_json(filename):
    with open(filename) as f:
        return json.load(f)


def write_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)


def truncate(str):
    if len(str) > 30:
        return str[:30]
    return str


def sanity_check(filename):
    print(filename)
    data = read_json(filename)
    if 'exam_id' not in data:
        print(filename + ' Missing exam_id')

    if 'topic' not in data or data['topic'] not in topics_list:
        print(filename + ' Invalid topic: ' + data['topic'])

    for ind, qn in enumerate(data['questions']):
        if 'question' not in qn or len(qn['question']) == 0 or type(qn['question']) is not str:
            print("Question text is missing " + str(ind))
            continue
        if 'options' not in qn or len(qn['options']) != 4:
            print(truncate(qn["question"]) + " Incorrect number of options")
        else:
            options = qn['options']
            for ind, opt in enumerate(options):
                for a in optionPrefix[ind]:
                    if type(opt) is not str:
                        print(truncate(qn["question"]) + " option is array")
                        continue
                    if opt.startswith(a):
                        qn['options'][ind] = opt.replace(a, '', 1)

        if 'correct_option' not in qn:
            print(truncate(qn["question"]) + " Option is missing")
        elif qn['correct_option'] not in correct_opt:
            if qn['correct_option'] in small_correct_opt:
                qn['correct_option'] = qn['correct_option'].upper()
            else:
                print(truncate(qn["question"]) + " Option is incorrect")

        if 'reasoning' not in qn and len(qn['reasoning']) == 0:
            print(truncate(qn["question"]) + " Detailed solution missing")

        if 'difficulty' not in qn:
            print(truncate(qn["question"]) + " Difficulty missing")

    write_json(data, filename)


def find_json_files(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".json"):
                sanity_check(os.path.join(root, file))


# Example usage:
directory_path = "gemini/gemini_output/sbi/reasoning"
json_files = find_json_files(directory_path)
