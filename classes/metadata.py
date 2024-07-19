from typing import List
class Metadata:
  def __init__(self, paragraphs: List[int], lines: List[int], sentences: List[int], imagePositions: List[int]):
    self.paragraphs = paragraphs
    self.lines = lines
    self.sentences = sentences
    self.imagePositions = imagePositions
  
  def __str__(self):
    return f"Paragraphs: {self.paragraphs}\nLines: {self.lines}\nSentences: {self.sentences}\nImage Positions: {self.imagePositions}"
  
  def jsonize(self) -> str:
    return str({
      "paragraphs": self.paragraphs,
      "lines": self.lines,
      "sentences": self.sentences,
      "imagePositions": self.imagePositions
    })