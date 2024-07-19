from classes.metadata import Metadata

class Passage:
  def __init__(self, text: str, header: str, source_details: str, questionNumbers: str , section: str, characterMetadata: Metadata, wordMetadata: Metadata):
    self.text = text
    self.images = []
    self.questionNumbers = questionNumbers
    self.section = section
    self.header = header
    self.source_details = source_details
    self.characterMetadata = characterMetadata
    self.wordMetadata = wordMetadata

  def __str__(self):
    return f"Header: {self.header}\nSource Details: {self.source_details}\nText: {self.text}\nQuestion Numbers: {self.questionNumbers}\nSection: {self.section}\nCharacter Metadata: {self.characterMetadata}\nWord Metadata: {self.wordMetadata}"

  def jsonize(self) -> str:
    return str({
      "text": self.text,
      "header": self.header,
      "source_details": self.source_details,
      "questionNumbers": self.questionNumbers,
      "section": self.section,
      "images": self.images,
      "characterMetadata": {
        "paragraphs": self.characterMetadata.paragraphs,
        "lines": self.characterMetadata.lines,
        "sentences": self.characterMetadata.sentences,
        "imagePositions": self.characterMetadata.imagePositions
      },
      "wordMetadata": {
        "paragraphs": self.wordMetadata.paragraphs,
        "lines": self.wordMetadata.lines,
        "sentences": self.wordMetadata.sentences,
        "imagePositions": self.wordMetadata.imagePositions
      }
    })

  def jsonifyMetadata(self):
    return str({
      "paragraphs": self.characterMetadata.paragraphs,
      "lines": self.characterMetadata.lines,
      "sentences": self.characterMetadata.sentences,
      "imagePositions": self.characterMetadata.imagePositions
    })