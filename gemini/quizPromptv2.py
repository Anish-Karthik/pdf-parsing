from threading import Thread
import time
import json

from commonQuizPrompt import *


def get_response_delayed_prompt(prompt, delay=1):
    time.sleep(delay)
    try:
        raw_response = model.generate_content([prompt])
        return raw_response.text
    except Exception as error:
        print(error)
        if "ResourceExhausted" in str(error):
            return get_response_delayed_prompt(prompt, delay * 2)
        else:
            return None


def get_question_prompt(topic, subtopic, difficulty):
    return get_response_delayed_prompt(f"""
        create a prompt to generate question description from {subtopic} in <topic>{topic}</topic> :

        the objective is to generate a valid and challenging question which helps the test takers improve their skills and learn.
        make sure the prompt's goal is to find a suitable type of question (define the exact structure of the question description as well) to evaluate a student's proficiency in the {topic}.
        the prompt should also contain an example.
        make the prompt understand the difficulty level: '{difficulty}' and creatively make the question '{difficulty}'.
        higher difficulty questions should mean the questions complex to solve. **Don't make the questions verbose based on difficulty level**.
        it should take the test takers more time to solve if the difficulty is high.
    """)


def get_quiz_json_prompt(topic, question_prompt, subtopic, skills, difficulty):
    return f"""
        {question_prompt}

        Topic:
        The questions should strictly be from the topic <topic>'{subtopic}'</topic>.

        It should Test the following skills:
        <skills>
        {skills}
        </skills>

        difficulty level: '{difficulty}' and creatively make the question '{difficulty}'.
        higher difficulty questions should mean the questions are more verbose.
        it should take the test takers more time to solve if the difficulty is high.

        <reasoning>
            The question belongs to the subtopic '{subtopic}' about <topic>'{topic}'</topic>.
            Give detailed explanation of why the answer is correct.
            Solve it step by step and teach the test takers.
            If additional context is available on the question description or the topic, provide that as well.
            The content should be useful for a student to learn and apply the same content for answering similar questions.
        </reasoning>

        <option and correct options>
            After doing the reasoning based on the final calculation, create 4 options and a correct option.
            Verify the correctness of the options. The correct option should be exact, not closest.
        </option and correct options>

        Output:
        give valid JSON
        {{
            "question": question_description,
            "difficulty": "easy" or "medium" or "hard",
            "reasoning": reasoning
        }}
    """


def add_options_to_json(question):
    return get_response_delayed_prompt(
        f"""
        Output:
        <question>
        {question["question"]}
        <reasoning>
        {question["reasoning"]}
        </reasoning>

        Identify the correct option from the reasoning and create 4 options and a correct option.
        Verify the correctness of the options.

        <rules>
        Options should directly answer the question asked, usually one word or number, maybe followed by a unit.
        </rules>

        give valid JSON
        {{
            "options": [
                option1,
                option2,
                option3,
                option4
            ],
            "correct_option": "A" or "B" or "C" or "D"
        }}
        """
    )


def json_parse(text):
    start = text.find("{")
    end = text.rfind("}")
    return json.loads(text[start:end + 1])


def valid_quiz_json(quiz_json):
    return all([
        isinstance(quiz_json.get("question"), str),
        quiz_json.get("question"),
        quiz_json.get("difficulty"),
        quiz_json.get("reasoning"),
        "options" in quiz_json and len(quiz_json["options"]) == 4,
        quiz_json.get("correct_option") in ["A", "B", "C", "D"]
    ])


def get_valid_quiz_json_recursive(topic, subtopic, difficulty, cnt=0):
    skills = ""
    question_prompt = get_question_prompt(topic, subtopic, difficulty)
    quiz_json_prompt = get_quiz_json_prompt(topic, question_prompt, subtopic, skills, difficulty)

    try:
        quiz_json_response_without_options = get_response_delayed_prompt(quiz_json_prompt)
        quiz_json = json_parse(quiz_json_response_without_options)
        quiz_json_response = add_options_to_json(quiz_json)
        options_json = json_parse(quiz_json_response)
        quiz_json["options"] = options_json["options"]
        quiz_json["correct_option"] = options_json["correct_option"]

        if not valid_quiz_json(quiz_json):
            raise ValueError("quizJson is not valid")

        if quiz_json != {}:
            questions.append(quiz_json)
    except Exception as error:
        if cnt > 2:
            return {}
        print(f"no. of recursive calls: {cnt}")
        print(f"question error: {error}")
        time.sleep(1)
        return get_valid_quiz_json_recursive(topic, subtopic, difficulty, cnt + 1)


def get_topics(topic):
    prompt = f"""
    Task:

    I want to learn {topic},
    create 25 subtopics so that I will be able to answer any {topic} questions under this topic,
    give the 25 subtopics as a python list.

    ensure it is a valid JSON:

    Format:
    List[{{"subtopic": subtopic1}}]
    """

    result = model.generate_content([prompt])
    return result.text


def get_valid_topics(topic):
    topics_text = get_topics(topic)

    try:
        start = topics_text.index("[")
        end = topics_text.rfind("]")
        topics_text = topics_text[start:end + 1]
        topics_list_json = json.loads(topics_text)

        if not any("subtopic" in topic for topic in topics_list_json):
            raise ValueError("topics_list_json does not contain subtopic")

        return topics_list_json

    except Exception as error:
        print(error)
        time.sleep(1)
        return get_valid_topics(topic)


difficulties = ["moderate 4/10", "above moderate 5/10", "very tricky 8/10"]


topics = [
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
]
for topic in topics:
    topics_json = get_valid_topics(f"{topic}")
    print(topics_json)
    questions = []

    for difficulty in difficulties:
        threads = []
        for sub_topic in topics_json:
            thread = Thread(target=get_valid_quiz_json_recursive, args=(f"{topic}", sub_topic["subtopic"], difficulty))
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()
    quiz = {}
    quiz["questions"] = questions
    quiz["title"] = "Logical Reasoning"
    quiz["topic"] = f"{topic}"
    quiz["exam_id"] = 17
    quiz["order"] = 2

    with open(f'gemini_output/new/sbi/reasoning/{topic}.json', 'w') as json_file:
        json.dump(quiz, json_file, indent=4)
