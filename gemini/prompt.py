

def get_prompt(json):

    writing_rules = """Grammar and usage: ask whether a word or phrase obeys the rules of Standard American English. They require you
  to understand the rules of verb and pronoun agreement, punctuation, modifier use, mood, voice, syntax, coordination, and idiom.

  Coherence and logical development:whether the sentences in a paragraph should be re-arranged, where a given sentence should be inserted, or whether a given sentence should be deleted.

  Clarity: ask whether a phrasing conveys an idea clearly and precisely.

  Style and tone: ask whether a word, phrase, or sentence is consistent in style and tone with other elements of the passage."""

    similar_questions = """Replace the referred word in the given in paranthesis:
  As the American population grows, ages, and gains better access to affordable health care insurance,
  the demand for primary medical services (are) expected to skyrocket.
  """

    prompt = f"""output: python list
    Generate exactly 15 SAT writing comprehension questions to test the user's English authoring skills for this passage that are clearly not reading comprehension,
    which tests the writer's ability to analyze and engage with complex texts. and avoid graph based quesions

    create questions to evaluate the following:{writing_rules}

    Example question: {similar_questions}


    From this Passage form questions: {json}

        format: [question,[op1,op2,op3,op4],correct_option("A" or "B" or "C" or "D")]

        return: list[question] output as python list"""

    return prompt
