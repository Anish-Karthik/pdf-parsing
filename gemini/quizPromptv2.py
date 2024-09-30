from threading import Thread
import time
import json
import traceback

from commonQuizPrompt import *


def get_response_delayed_prompt(prompt, delay=1):
    time.sleep(delay)
    try:
        raw_response = model.generate_content([prompt])
        return raw_response.text
    except Exception as error:
        print(traceback.format_exc())
        if "ResourceExhausted" in str(error):
            return get_response_delayed_prompt(prompt, delay * 2)
        else:
            return None


def get_pro_response(prompt, delay=0.1):
    time.sleep(delay)
    try:
        raw_response = model_pro.generate_content([prompt])
        return raw_response.text
    except Exception as error:
        print(traceback.format_exc())
        if "ResourceExhausted" in str(error):
            return get_pro_response(prompt, delay * 2)
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

        <question>
        difficulty level: '{difficulty}' and creatively make the question '{difficulty}'.
        higher difficulty questions should mean the questions are more verbose.
        it should take the test takers more time to solve if the difficulty is high.

        Verify that the question is logically and mathematically correct
        </question>

        <reasoning>
            The question belongs to the subtopic '{subtopic}' about <topic>'{topic}'</topic>.
            Give detailed explanation of why the answer is correct.
            Solve the above question step by step reviewing each step is correct and valid.
            Each step should be explained in detail and step by step and is very important.
            verify the mathematical calulations and every logical reasoning is correct.
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


def get_pro_reasoning(question):
    return model_pro.generate_content(
        f"""
        <question>
        {question["question"]}
        </question>

        Solve the above question step by step reviewing each step is correct and valid.
        Each step should be explained in detail and step by step and is very important.

        verify the mathematical calulations and every logical reasoning is correct.

        """
    ).text


def add_options_to_json(question):
    return get_response_delayed_prompt(
        f"""
        Output:
        <question>
            {question}
        </question>

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
        quiz_json.get("question"),
        isinstance(quiz_json.get("question"), str),
        quiz_json.get("difficulty"),
        quiz_json.get("reasoning"),
        "options" in quiz_json and len(quiz_json["options"]) == 4,
        quiz_json.get("correct_option") in ["A", "B", "C", "D"]
    ])


def json_to_markdown(json_obj, indent_level=0):
    markdown = ""
    indent = "  " * indent_level  # 2 spaces per indent level

    if isinstance(json_obj, dict):
        for key, value in json_obj.items():
            markdown += f"{indent}**{key}**: "
            if isinstance(value, (dict, list)):
                markdown += "\n" + json_to_markdown(value, indent_level + 1)
            else:
                markdown += f"{value}\n"
    elif isinstance(json_obj, list):
        for item in json_obj:
            markdown += f"{indent}- "
            if isinstance(item, (dict, list)):
                markdown += "\n" + json_to_markdown(item, indent_level + 1)
            else:
                markdown += f"{item}\n"
    else:
        markdown += f"{json_obj}\n"
    
    return str(markdown) 


def get_valid_quiz_json_recursive(topic, subtopic, difficulty, difficulty_value, cnt=0):
    skills = ""
    question_prompt = get_question_prompt(topic, subtopic, difficulty)
    quiz_json_prompt = get_quiz_json_prompt(topic, question_prompt, subtopic, skills, difficulty)
    option_map = {"0": "A", "1": "B", "2": "C", "3": "D"}

    question_json_response_without_options = ""
    question_json_response = ""

    try:
        question_json_response_without_options = get_pro_response(quiz_json_prompt)
        question_json = json_parse(question_json_response_without_options)

        question_json_response = add_options_to_json(question_json)
        options_json = json_parse(question_json_response)
        question_json["difficulty"] = difficulty_value
        question_json["options"] = options_json["options"]
        question_json["correct_option"] = options_json["correct_option"]
        
        if not isinstance(question_json["question"], str):
            question_json["question"] = json_to_markdown(question_json["question"])

        if not isinstance(question_json["reasoning"], str):
            question_json["reasoning"] = json_to_markdown(question_json["reasoning"])

        if not question_json["correct_option"] in ["A", "B", "C", "D"]:
            for ind,option in enumerate(question_json["options"]):
                if question_json["correct_option"] in option:
                    question_json["correct_option"] = option_map[str(ind)]

        if not valid_quiz_json(question_json):
            print(question_json)
            raise ValueError("quizJson is not valid")

        if question_json != {}:
            questions.append(question_json)
    except Exception as error:
        if cnt > 2:
            return {}
        print(f"no. of recursive calls: {cnt}")
        print(f"question error: {error}")

        error_question_json = {
            "question": question_json_response_without_options,
            "option": question_json_response,
        }
        error_questions.append(error_question_json)
        traceback.print_exc()

        time.sleep(1)
        return get_valid_quiz_json_recursive(topic, subtopic, difficulty, cnt + 1)


def get_topics(topic):
    prompt = f"""
    Task:

    I want to learn **{topic}**,
    create 15 diversed subtopics so that I will be able to answer any {topic} questions,
    Make sure that the subtopics do not overlap much.
    give the 15 subtopics as a python list.

    ensure it is a valid JSON:

    Format:
    List[{{"subtopic": subtopic1}}]
    """

    result = model_pro.generate_content([prompt])
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


difficulties = {
    "easy 5/10": "easy",
    "easy 6/10": "medium",
    "medium 5/10": "medium",
    "medium 6/10": "medium",
    "tricky 8/10": "hard"
}
model_pro = generativeai.GenerativeModel(
    model_name="gemini-1.5-pro"
)

topics = [
    # "Quants - Number Systems",
    # "Quants - Simplification and Approximation",
    # "Quants - Data Interpretation",
    # "Quants - Quadratic Equations",
    # "Quants - Profit and Loss",
    # "Quants - Simple Interest and Compound Interest",
    # "Quants - Time and Work",
    # "Quants - Time, Distance, and Speed",
    # "Quants - Mensuration",
    "Quants - Average",
    # "Quants - Ratio and Proportion",
    # "Quants - Partnership",
    # "Quants - Mixtures and Alligations",
    # "Quants - Permutation and Combination",
    # "Quants - Probability",
    # "Quants - Data Sufficiency",
    # "Quants - Inequalities",
    # "Quants - Logarithms",
    # "Quants - Surds and Indices",
    # "Quants - Coordinate Geometry",
    # "Quants - Trigonometry",
    # "Quants - Algebra",
    # "Quants - Geometry",
    # "Quants - Calculus",
]

reasoning_topics = [
    # "Logical Reasoning - Alphanumeric Series",
    # "Logical Reasoning - Ranking Direction Alphabet Test",
    # "Logical Reasoning - Data Sufficiency",
    # "Logical Reasoning - Coded Inequalities",
    # "Logical Reasoning - Seating Arrangement",
    # "Logical Reasoning - Puzzle",
    # "Logical Reasoning - Syllogism",
    # "Logical Reasoning - Clocks",
    # "Logical Reasoning - Blood Relations",
    # "Logical Reasoning - Input-Output",
    # "Logical Reasoning - Coding-Decoding",
    # "Logical Reasoning - Calendars",
    # "Logical Reasoning - Dice",
    # "Logical Reasoning - Cube and Cuboid",
    # "Logical Reasoning - Truth Tables",
    # "Logical Reasoning - Ranking-Direction-Alphabet Test",
]

for order, topic in enumerate(topics):
    topics_json = get_valid_topics(f"{topic}")
    print(topics_json)
    questions = []
    error_questions = []

    for difficulty, difficulty_value in difficulties.items():
        threads = []
        for sub_topic in topics_json:
            thread = Thread(target=get_valid_quiz_json_recursive, args=(f"{topic}", sub_topic["subtopic"], difficulty, difficulty_value))
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()
    quiz = {}
    quiz["questions"] = questions
    quiz["title"] = "Quantitative Ability"
    quiz["topic"] = f"{topic}"
    quiz["exam_id"] = 18
    quiz["order"] = order

    
    if not os.path.exists(f'gemini_output/new/sbi/quants'):
        os.mkdir(f'gemini_output/new/sbi/quants')
    with open(f'gemini_output/new/sbi/quants/{topic}.json', 'w') as json_file:
        json.dump(quiz, json_file, indent=4)

    quiz["questions"] = error_questions
    if not os.path.exists(f'gemini_output/error/sbi/quants'):
        os.mkdir(f'gemini_output/error/sbi/quants')
    with open(f'gemini_output/error/sbi/quants/{topic}.json', 'w') as json_file:
        json.dump(quiz, json_file, indent=4)

# def get_pro_questions(quiz_json, cnt=0):
#     try:
#         reasoning_response = get_pro_reasoning(quiz_json)
#         print(reasoning_response)
#         quiz_json["superior_reasoning"] = reasoning_response
#         quiz_json_response = add_options_to_json(quiz_json)
#         options_json = json_parse(quiz_json_response)
#         quiz_json["options"] = options_json["options"]
#         quiz_json["correct_option"] = options_json["correct_option"]

#         if not valid_quiz_json(quiz_json):
#             raise ValueError("quizJson is not valid")

#         if quiz_json != {}:
#             questions.append(quiz_json)
#     except Exception as error:
#         if cnt > 2:
#             return {}
#         print(f"no. of recursive calls: {cnt}")
#         print(f"question error: {error}")
#         print(traceback.format_exc())
#         time.sleep(1)
#         return get_pro_questions(question, cnt + 1)


# path = "gemini_output/new/sbi/reasoning/Logical Reasoning - Alphanumeric Series.json"

# with open(path, 'r') as json_file:
#     data = json.load(json_file)
#     print(len(data["questions"]))
#     for data_questions_batch in split_into_batches(data["questions"], 10):
#         threads = []
#         for question in data_questions_batch:
#             print(question)
#             thread = Thread(target=get_pro_questions, args=(question,))
#             threads.append(thread)
#             thread.start()
#         for thread in threads:
#             thread.join()

#     data["questions"] = questions

# with open(path, 'w') as json_file:
#     json.dump(data, json_file, indent=4)
