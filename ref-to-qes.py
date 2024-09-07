from typing import List, Optional
import os
import json

from model import Option, Passage, PassageLink, Question, ReadingComprehension, Reference

# Directory containing JSON files
def mergeReferencesWithPassage(readingComprehension: ReadingComprehension):
    passage_links = []
    for qid, question in enumerate(readingComprehension.questions):
        for opt_index, option in enumerate(question.options):
            if option.reference is not None and option.reference.start_word is not None and option.reference.end_word is not None:
                passage_links.append(PassageLink(question=qid, option=opt_index, word_index=option.reference.start_word, is_start=True, is_header=False))
                passage_links.append(PassageLink(question=qid, option=opt_index, word_index=option.reference.end_word + 1, is_start=False, is_header=False))

        for reference in question.references:
            passage_links.append(PassageLink(question=qid, option=None, word_index=reference.start_word, is_start=True, is_header=False))
            passage_links.append(PassageLink(question=qid, option=None, word_index=reference.end_word + 1, is_start=False, is_header=False))

    for ref in readingComprehension.subheading_references:
        passage_links.append(PassageLink(question=qid, option=None, word_index=ref.start_word, is_start=True, is_header=True))
        passage_links.append(PassageLink(question=qid, option=None, word_index=ref.end_word + 1, is_start=False, is_header=True))

    passage_links = sorted(passage_links, key=lambda link: link.word_index)
    passage_links.reverse()

    passage_words = readingComprehension.passage.passage.strip().split(" ")
    for link in passage_links:
        passage_words.insert(link.word_index, link.link())

    readingComprehension.passage.passage = " ".join(passage_words)

def json_to_reading_comprehension(json_data):
    passage = Passage(json_data['passage'])
    questions = []
    
    for q in json_data['questions']:
        options = []
        for option in q['options']:
            if option['reference'] is not None:
                options.append(Option(option['description'], Reference(option['reference']['start_word'], option['reference']['end_word'])))
            else:
                options.append(Option(option['description']))
        question = Question(
            qno=q['qno'],
            description=q['description'],
            options=options,
            correct_option=q.get('correct_option'),
            detailed_answer=q.get('detailed_answer')
        )
        if 'references' in q:
            question.references = [Reference(ref['start_word'], ref['end_word']) for ref in q['references']]
        questions.append(question)
    
    header = json_data['header']
    section = json_data.get('section', 1)
    
    reading_comprehension = ReadingComprehension(passage, questions, header, section)
    
    if 'subheading_references' in json_data:
        reading_comprehension.subheading_references = [
            Reference(ref['start_word'], ref['end_word']) for ref in json_data['subheading_references']
        ]
    
    return reading_comprehension
# Iterate over each file in the sorted list
import json
import os

import json
import os

directory = "sat/outputJSON"

json_files = sorted([f for f in os.listdir(directory) if f.endswith('.json')])

for filename in json_files:
    file_path = os.path.join(directory, filename)
    
    try:
        with open(file_path, 'r') as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON in file {filename}: {e}")
                # Optionally, print file content or skip to the next file
                with open(file_path, 'r') as f:
                    print(f.read())
                continue  # Skip to the next file if there is an error
            
            # Convert JSON to ReadingComprehension object
            reading_comprehension = json_to_reading_comprehension(data)
            
            # Call the method to process the passage
            mergeReferencesWithPassage(reading_comprehension)
            
            # Update the passage in the JSON data
            data["passage"] = str(reading_comprehension.passage)
            
            # Write the updated data back to the JSON file
            with open(file_path, 'w') as file:
                json.dump(data, file, indent=4)
            
            print(f"Processed {filename} and merged references.")
    
    except Exception as e:
        print(f"An error occurred with file {filename}: {e}")
