from typing import List, Optional
import json

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
  def __init__(self, passage: Passage, questions: List[Question], section: int = 1):
    self.passage = passage
    self.questions = questions
    self.section = section
    self.header = None

  def to_json(self):
    if self.header:
      return {
        "section": self.section,
        "header": self.header,
        "passage": self.passage.to_json(),
        "questions": [question.to_json() for question in self.questions]
      }
    return {
      "section": self.section,
      "passage": self.passage.to_json(),
      "questions": [question.to_json() for question in self.questions]
    }

  def __str__(self):
    return f"Passage: {self.passage.passage}\nQuestions: {self.questions}"
