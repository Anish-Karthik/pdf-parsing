from gemini_api import *
from content import *
import re
import time
from google.api_core.exceptions import ResourceExhausted
import json

exam = "IBPS PO, SBI PO banking exams"
# sample_questions = neet_biology_questions
difficulties = ["easy","medium","hard"]
topics = [
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


def get_detailed_solution(json,subtopic):
    return get_response_delayed_prompt(f"""
    question: {json}

    The question belongs to the topic '{subtopic}' to prepare for {exam}. Give detailed explanation why the answer is correct.

    If there are additional context available on the question description or the topic, provide them as well.
    The content should be useful for a student to learn and apply the same content for answering similar questions.

    The solution should be relevant to a anyone in india who is preparing for exams like {exam}.

    Output:
    Detailed Explanation: "detailed explanation of the answer"
    """)

def get_subtopic(topic):
    subtopics_list = get_response_delayed_prompt(
        f"""
        Task:

        i want to learn {topic} in mathematics to clear banking exams,
        create 50 subtopics so that i will be able to any {topic} questions under this topic,
        give the 50 subtopics as a python list

        ensure it is a valid json:

        """+"""Format:
        List[{"subtopics": subtopic1}]"""+f"""
        Sample Questions:
        {sample_questions}
        """
    )
    print(filter_response(subtopics_list))

    return json.loads(filter_response_as_list(subtopics_list))

def get_question_prompt(topic,difficulty):
    return get_response_delayed_prompt(
        f""" 
        Sample prompt:
        
        create a question with multiple choice with atleast two lines.
        verify objective type with its correct answer and provide reasoning for the correct answer and why other options are wrong. 
        verify everything is correct

    Task:
    
    create a prompt to generate question from {topic}:
    
    the new prompt should be based on the sample prompt but the objective is to generate questions from {topic}.
    make sure the prompt's goal is to find a suitable type of question (define the exact structure of the question description as well) to evaluate a student's profeciency in the {topic}
    the prompt should also contain an example as well.
    make the prompt understand the difficulty level : '{difficulty}' and creatively make the question '{difficulty}'
    higher difficulty questions should mean the questions are more verbose.
    it should take the test takers more time to solve if the difficulty is high.
   """
    )

def get_quiz_json_prompt(question_prompt,subtopic,skills,difficulty):
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

    """+"""
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


def get_response_delayed_prompt(prompt,delay=1):
    try:
        print(delay)
        time.sleep(delay)
        print("delay ended")
        raw_response = model.generate_content(
            prompt
        )
        print("call ended")
        # print(raw_response.text)
        return raw_response.text
    except ResourceExhausted as e:
        print("delay:", delay, e)
        return get_response_delayed_prompt(prompt,delay * 2)
    except Exception as e:
        print(e)
        return None


def filter_response(text):
    text = re.sub("\*{2,}","",text)
    print("####")
    text = text[text.index("{"):text.rindex("}") + 1]
    print(text)
    return text
  
def filter_response_as_list(text):
    text = re.sub("\*{2,}","",text)
    return text[text.index("["):text.rindex("]") + 1]



api_key = os.getenv("GEMINI_API_KEY")
configure_client(api_key)

model = generativeai.GenerativeModel(
    model_name="gemini-1.5-flash"
)

all_qns_json = []


# sample_questions = input("Enter sample questions: ")

for topic in topics:
    for difficulty in difficulties:
        subtopics = get_subtopic(topic)

        for subtopic in subtopics[3:]:
            skills = get_response_delayed_prompt(f"""what skills does these {subtopic} test in {exam}.""")
            question_prompt = get_question_prompt(subtopic,difficulty)
            print(question_prompt,subtopics,skills)
            json_text = filter_response(
                    get_response_delayed_prompt(
                        get_quiz_json_prompt(question_prompt,subtopic["subtopics"],skills,difficulty)
                    )
                )

            if json_text is None:
                continue

            try:
                qns_json = json.loads(json_text)
                for qn_json in qns_json:
                    qn_json["reasoning"] = get_detailed_solution(json_text,subtopic)
                    all_qns_json.append(qn_json)
                    print(str(qn_json)+"\n\n\n")
            except Exception as e:
                print("why")
                print(e)
                
        final_qns_json = []
        for qn_obj in all_qns_json:
            final_qns_json.append({
                "question": qn_obj["question"],
                "options": qn_obj["options"],
                "correct_option": qn_obj["correct_option"],
                "difficulty": difficulty,
                "detailed_solution": qn_obj["reasoning"]
            })
        with open('output/final_test.json', 'w') as json_file:
            json.dump(final_qns_json, json_file, indent=4)

    
  
  

