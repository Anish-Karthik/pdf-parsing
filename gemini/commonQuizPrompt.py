from gemini_api import *
from content import *
import re
import time
from google.api_core.exceptions import ResourceExhausted
import json
import traceback
import threading

exam = "IBPS PO, SBI PO banking exams"
title = ""
# sample_questions = neet_biology_questions
difficulties = ["easy", "medium", "hard"]
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

fill_ups_topics = [
    "Tenses: Present simple, present continuous, present perfect, present perfect continuous, past simple, past continuous, past perfect, past perfect continuous, future simple, future continuous, future perfect, future perfect continuous",
    "Modals: Can, could, may, might, must, should, ought to, will, would, shall",
    "Articles: A, an, the",
    "Prepositions: In, on, at, for, of, to, by, with, from, etc.",
    "Conjunctions: And, but, or, because, so, if, when, etc.",
    "Adjectives and adverbs: Comparative and superlative forms",
    "Pronouns: Personal, possessive, reflexive, demonstrative, relative, interrogative",
    "Subject-verb agreement: Singular and plural forms",
    "Sentence structure: Active and passive voice, direct and indirect speech",
    "Vocabulary: Synonyms and antonyms: Words with similar or opposite meanings",
    "Vocabulary: Phrasal verbs: Verbs combined with prepositions or adverbs",
    "Vocabulary: Idioms and proverbs: Expressions with figurative meanings",
    "Vocabulary: Collocations: Words that are often used together",
    "Vocabulary: One-word substitutes: Single words that can replace phrases or clauses"
]

para_jumbles_topics = [
    "Paragraph coherence: Understanding the overall theme and flow of the paragraph",
    "Logical sequencing: Identifying the correct order of sentences based on cause-and-effect relationships, chronological order, or thematic progression",
    "Topic sentences: Identifying the main idea of the paragraph",
    "Supporting details: Understanding how supporting sentences relate to the topic sentence",
    "Conjunctions and transition words: Recognizing the role of connectors in establishing relationships between sentences",
    "Contextual clues: Using hints and clues within the paragraph to determine the correct sequence",
    "Sentence structure and grammar: Understanding how sentence structure and grammar affect the overall coherence and flow"
]


def get_detailed_solution(json, subtopic):
    return get_response_delayed_prompt(f"""
    question: {json}

    The question belongs to the topic '{subtopic}' to prepare for {exam}. Give detailed explanation why the answer is correct.

    If there are additional context available on the question description or the topic, provide them as well.
    The content should be useful for a student to learn and apply the same content for answering similar questions.

    The solution should be relevant to a anyone in india who is preparing for exams like {exam}.

    Output:
    Detailed Explanation: "detailed explanation of the answer"
    """)

def get_subtopic_english(topic):
    subtopics_list = get_response_delayed_prompt(
        f"""
        Task:

        i want to learn {topic} in english to clear banking exams,
        create 50 subtopics so that i will be able to any {topic} questions under this topic,
        give the 50 subtopics as a python list

        ensure it is a valid json:

        """ + """Format:
        List[{"subtopic": subtopic1}]""" + f"""
        Sample Questions:
        {sample_questions}
        """
    )
    print(filter_response(subtopics_list))

    try:
        return json.loads(filter_response_as_list(subtopics_list))
    except Exception as e:
        return []

def get_subtopic_math(topic):
    subtopics_list = get_response_delayed_prompt(
        f"""
        Task:

        i want to learn {topic} in mathematics to clear banking exams,
        create 50 subtopics so that i will be able to any {topic} questions under this topic,
        give the 50 subtopics as a python list

        ensure it is a valid json:

        """ + """Format:
        List[{"subtopic": subtopic1}]""" + f"""
        Sample Questions:
        {sample_questions}
        """
    )
    print(filter_response(subtopics_list))

    try:
        return json.loads(filter_response_as_list(subtopics_list))
    except Exception as e:
        return []


def get_question_prompt(topic, difficulty):
    return get_response_delayed_prompt(
        f"""
        Sample prompt:

        create a question with multiple choice with atleast two lines.
        verify objective type with its correct answer and provide reasoning for the correct answer and why other options are wrong.
        verify everything is correct

    Task:

    create a prompt to generate question from {topic} :

    the new prompt should be based on the sample prompt but the objective is to generate questions from {topic}.
    make sure the prompt's goal is to find a suitable type of question (define the exact structure of the question description as well) to evaluate a student's profeciency in the {topic}
    the prompt should also contain an example as well.
    make the prompt understand the difficulty level : '{difficulty}' and creatively make the question '{difficulty}'
    higher difficulty questions should mean the questions are more verbose.
    it should take the test takers more time to solve if the difficulty is high.
   """
    )

def get_fill_ups_question_prompt(topic, difficulty):
    return get_response_delayed_prompt(
        f"""
        Sample prompt:

        create a fill in the blanks type question with multiple choice with atleast two lines.
        verify objective type with its correct answer and provide reasoning for the correct answer and why other options are wrong.
        verify everything is correct

    Task:

    create a prompt to generate fill in the blanks type question from {topic} :

    the new prompt should be based on the sample prompt but the objective is to generate questions from {topic}.
    make sure the prompt's goal is to find a suitable type of question (define the exact structure of the question description as well) to evaluate a student's profeciency in the {topic}
    the prompt should also contain an example as well.
    make the prompt understand the difficulty level : '{difficulty}' and creatively make the question '{difficulty}'
    higher difficulty questions should mean the questions are more verbose.
    it should take the test takers more time to solve if the difficulty is high.
   """
    )

def get_para_jumbles_question_prompt(topic, difficulty):
    return get_response_delayed_prompt(
        f"""
        Sample prompt:

        create a jumbled paragraphs type question with multiple choice (where each choice is a jumbled arrangement order) with atleast two lines.
        verify objective type with its correct answer and provide reasoning for the correct answer and why other options are wrong.
        verify everything is correct

    Task:

    create a prompt to generate jumbled paragraphs type question from {topic} :

    the new prompt should be based on the sample prompt but the objective is to generate questions from {topic}.
    make sure the prompt's goal is to find a suitable type of question (define the exact structure of the question description as well) to evaluate a student's profeciency in the {topic}
    the prompt should also contain an example as well.
    make the prompt understand the difficulty level : '{difficulty}' and creatively make the question '{difficulty}'
    higher difficulty questions should mean the questions are more verbose.
    it should take the test takers more time to solve if the difficulty is high.
   """
    )

def get_error_correction_question_prompt(topic, difficulty):
    return get_response_delayed_prompt(
        f"""
        Sample prompt:

        create an error correction question with multiple choice with atleast two lines.
        verify objective type with its correct answer and provide reasoning for the correct answer and why other options are wrong.
        verify everything is correct

    Task:

    create a prompt to generate error correction type question from {topic} :

    the new prompt should be based on the sample prompt but the objective is to generate questions from {topic}.
    make sure the prompt's goal is to find a suitable type of question (define the exact structure of the question description as well) to evaluate a student's profeciency in the {topic}
    the prompt should also contain an example as well.
    make the prompt understand the difficulty level : '{difficulty}' and creatively make the question '{difficulty}'
    higher difficulty questions should mean the questions are more verbose.
    it should take the test takers more time to solve if the difficulty is high.
   """
    )


def get_quiz_json_prompt(question_prompt, subtopic, skills, difficulty):
    return f"""
      {question_prompt}

      Topic:
      The questions should strictly be from the topic <topic>'{subtopic}'</topic>.

      It should Test the following skills:
      <skills>
      {skills}
      </skills>

      difficulty level : '{difficulty}' and creatively make the question '{difficulty}'
    higher difficulty questions should mean the questions are more verbose.
    it should take the test takers more time to solve if the difficulty is high.

    """ + """
      Output:
      give python
      {
            "question":question_description,
            "options":[option1,option2,option3,option4],
            "correct_option":("A" or "B" or "C" or "D"),
            "reasoning":reasoning
      }
  give python output
  """


def get_response_delayed_prompt(prompt, delay=0.1):
    try:
        time.sleep(delay)
        raw_response = model.generate_content(
            prompt
        )
        return raw_response.text
    except ResourceExhausted as e:
        print(traceback.format_exc())
        return get_response_delayed_prompt(prompt, delay * 2)
    except Exception as e:
        print(traceback.format_exc())
        return None


def filter_response(text):
    text = re.sub("\\*{2,}", "", text)
    text = text[text.index("{"):text.rindex("}") + 1]
    return text


def get_subtopic_question(subtopic, difficulty, quiz_questions):
    skills = get_response_delayed_prompt(f"""what skills does these {subtopic} test in {exam}.""")
    question_prompt = get_para_jumbles_question_prompt(subtopic, difficulty)

    json_text = filter_response(
        get_response_delayed_prompt(
            get_quiz_json_prompt(question_prompt, subtopic, skills, difficulty)
        )
    )

    print(subtopic)

    if json_text is None:
        return

    try:
        qn_json = json.loads(json_text)
        qn_json["reasoning"] = get_detailed_solution(json_text, subtopic)
        qn_json["difficulty"] = difficulty
        quiz_questions.append(
            qn_json
        )
        print(subtopic, "question added")
    except Exception as e:
        print(e)


def filter_response_as_list(text):
    text = re.sub("\\*{2,}", "", text)
    return text[text.index("["):text.rindex("]") + 1]


def split_into_batches(array, batch_size=5):
    return [array[i:i + batch_size] for i in range(0, len(array), batch_size)]


quizzes = []


def get_quiz_json(topic):
    global quizzes
    quiz = dict()
    quiz_questions = []

    subtopics = get_subtopic_english(topic)
    for difficulty in difficulties:
        print(difficulty)

        threads = []
        for subtopic in subtopics:
            thread = threading.Thread(target=get_subtopic_question, args=(subtopic["subtopic"], difficulty, quiz_questions))
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()

    quiz["topic"] = topic
    quiz["questions"] = quiz_questions
    quiz["title"] = title

    with open(f'output/para_jumbles/{topic}.json', 'w') as json_file:
        json.dump(quiz, json_file, indent=4)


api_key = os.getenv("GEMINI_API_KEY")
configure_client(api_key)

model = generativeai.GenerativeModel(
    model_name="gemini-1.5-flash"
)


# sample_questions = input("Enter sample questions: ")
# for topic in topics:
#     get_quiz_json(topic)
