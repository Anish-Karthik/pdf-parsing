from typing import List, Optional
from typing import TypedDict


class Option(TypedDict):
  description: str

class Question(TypedDict):
  qno: int
  description: str
  options: List[Option]
  correct_option: str
  detailed_answer: str
  