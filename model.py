from typing import List, Optional
import json


class PassageLink:
    def __init__(self, question: int, option: int, word_index: int, is_start: bool):
        self.question = question
        self.option = option
        self.word_index = word_index
        self.is_start = is_start

    def link(self):
        if self.is_start:
            link = "QS$$" + str(self.question)
        else:
            link = "QE$$" + str(self.question)
        if self.option is not None:
            if self.is_start:
                link += ("OS$$" + str(self.option))
            else:
                link += ("OE$$" + str(self.option))
        return link


class Reference:
    def __init__(self, start_word: int, end_word: int):
        self.start_word = start_word
        self.end_word = end_word

    def to_json(self):
        return {
            "start_word": self.start_word,
            "end_word": self.end_word
        }

    def __str__(self):
        return f"Start Word: {self.start_word}, End Word: {self.end_word}"


class Option:
    def __init__(self, description: str):
        self.description = description
        self.reference: Optional[Reference] = None

    def to_json(self):
        return {
            "description": self.description,
            "reference": self.reference.to_json() if self.reference else None
        }


class Question:
    def __init__(self, qno: int, description: str, options: List[Option], correct_option: Optional[str] = None, detailed_answer: Optional[str] = None):
        self.qno = qno
        self.description = description
        self.options = options
        self.correct_option = correct_option
        self.detailed_answer = detailed_answer
        self.references: List[Reference] = []

    def to_json(self):
        return {
            "qno": self.qno,
            "description": self.description,
            "options": [option.to_json() for option in self.options],
            "correct_option": self.correct_option,
            "detailed_answer": self.detailed_answer,
            "references": [reference.to_json() for reference in self.references]
        }

    def __str__(self) -> str:
        return f"Q{self.qno}: {self.description}\nOptions: {self.options}\nCorrect Option: {self.correct_option}"


class Passage:
    def __init__(self, passage: str):
        self.passage = passage

    def to_json(self):
        return self.passage

    def __str__(self) -> str:
        return self.passage


class ReadingComprehension:
    def __init__(self, passage: Passage, questions: List[Question], header: str, section: int = 1):
        self.passage = passage
        self.questions = questions
        self.subheading_references: List[Reference] = []
        self.header = header
        self.section = section

    def to_json(self):
        return {
            "section": self.section,
            "passage": self.passage.to_json(),
            "header": self.header,
            "subheading_references": [reference.to_json() for reference in self.subheading_references],
            "questions": [question.to_json() for question in self.questions]
        }

    def __str__(self):
        return f"Passage: {self.passage.passage}\nQuestions: {self.questions}"
