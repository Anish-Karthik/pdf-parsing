from typing import List,Tuple
from dataclasses import dataclass
import fitz
import re
import pandas as pd
# import numpy as np

qnList = []
desc = ""
op = ["","","",""]


def init():
    global desc
    global op
    desc = ""
    op = ["","","",""]

class Questionnare:
    def _init_(self,description,op1,op2,op3,op4) -> None:
        self.description = description
        self.op1 = op1
        self.op2 = op2
        self.op3 = op3
        self.op4 = op4

def isquestionare(hpos,element) -> bool:
    for i in hpos:
        if ((element[0] >= i+17 and element[0] <= i + 18) or element[0] == i):
            return True
    return False

def isnextqn(element, prev):
    return abs(prev[1]-element[1]) > 50 or abs(prev[0]-element[0]) > 50

def isanoption(element) -> bool:
    return re.search(r"(?<!.)[A-D]\) ", element[4])


def removenextline(text: str) -> str:
    return re.sub(r"\n"," ",text)

def extract_text_from_pdf(pdf_file: str) -> list:
    layout= []

    doc = fitz.open(pdf_file)

    for page in doc:
        layout.append("\n")
        hpos = set() 

        blocks = page.get_text("blocks") 
        for block in blocks:
            if isanoption(block): #check if it's an option
                hpos.add(block[0])
        prev = None
        for block in blocks:
            if prev == None:
                prev = block
            if not (isquestionare(hpos,block) and len(block[4]) < 200):
                if re.match(r"^\d{1,}\n",block[4]):
                    # print(block[4])
                    continue
                # remove starting dots
                if re.match(r"^\.{1,}",block[4]):
                    # print(block[4])
                    continue
                if re.match(r"Line\n5|(Line\n)",block[4]):
                    # print(block[4])
                    continue
                if re.match(r"(Unauthorized copying or reuse of any part of this page is illegal.)|(CO NTI N U E)|(STOP)", block[4]):
                    # print(block[4])
                    continue
                # if isnextqn(block,prev):
                #     layout.append("\n")
                layout.append(block[4])
                prev = block
    # print(len(layout))
    return layout
    
def write_text_to_file(text: str, file_path: str) -> None:
    with open(file_path, "w", encoding="UTF-8") as f:
        f.write(text)


class PassageUtils:
  @staticmethod
  def split_passages(text: str) -> list:
    passages = re.split(r"(Questions \d*-\d*(.|\n)*?)(?=[A-Z])", text)
    return passages
  
  @staticmethod
  def extract_noise(passages: list) -> list:
    crct = []
    for i in range(len(passages)):
      if i == 0:
        continue
      if len(passages[i]) <= 2:
        continue
      crct.append(passages[i])
    return crct
  
  @staticmethod
  def merge_passages(passages: list) -> list:
    crct = []
    for i in range(0, len(passages), 2):
      crct.append(passages[i] + passages[i + 1])
    return crct
  def pre_process_passages(all_text: str) -> list:
    passages = PassageUtils.split_passages(all_text)
    passages = PassageUtils.extract_noise(passages)
    passages = PassageUtils.merge_passages(passages)
    return passages


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


@dataclass
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
def extract_header(passage: str) -> str:
  tmp = re.match(r"(Questions \d*-\d*(.|\n)*?(?=[A-Z]))", passage)
  if tmp is None:
    return "No header found"
  return tmp.group()

def extract_data(passage: str, header: str) -> str:
  return passage.replace(header, "").strip()

def extract_question_numbers(header: str) -> str:
  tmp = re.findall(r"\d*-\d*", header)
  if tmp is None or len(tmp) == 0:
    return "No question numbers found"
  return tmp[0]

def extract_source_details(data: str) -> str:
  tmp = re.match(r"(((This passage is)|(Passage \d{1,})) (((?:.|\n)*?\.\n)|((?:.|\n)*?\.){3}))", data)
  if tmp is None:
    return "No source details found"
  return tmp.group()

def strip_excess_whitespace_paragraphs(data: str) -> str:
  # strip out the leading and trailing whitespaces
  # replace all the whitespace followed by \n\t till the first non-whitespace character
  data = re.sub(r"\s+\n\t(?=\S)", r"\n\t", data)
  # replace all the whitespace followed by non-whitespace character till the first \n\t
  data = re.sub(r"\s+(?=\S+\n\t)", r"", data)
  return data

def extract_character_metadata(data: str) -> Tuple[str, Metadata]:
  # replace all the patten matching with this regex (\.|\?)\n with (\.|\?)\n\t
  data = re.sub(r"(\.|\?)\n", r"\1\n\t", data)
  # data = strip_excess_whitespace_paragraphs(data)
  lines = [0] + [m.end(0) for m in re.finditer(r"\n", data)]
  paragraphs = [0] + [m.end(0)-1 for m in re.finditer(r"(\.|\?)\n\t", data)]
  # replace all the \n with " ", which are not followed by \t
  data = re.sub(r"\n(?!\t)", r" ", data)
  sentences = [0] + [m.end(0) for m in re.finditer(r"\. ", data)]
  return data, Metadata(paragraphs, lines, sentences, [])

class Word:
    def __init__(self, word: str, start: int, end: int, pos: int):
        self.word = word
        self.start = start
        self.end = end
        self.pos = pos # denoting the position of the word in the data

    @staticmethod
    def from_string(word: str, start: int, pos: int):
        return Word(word, start, start + len(word), pos)
    
class WordList:
    def __init__(self, data: str):
        self.words = WordUtils.extract_words(data)
        self.wordMap = {}
        self.data = data
        for word in self.words:
            self.wordMap[word.start] = word.pos
        

    def formWordMetadata(self, charMetadata: Metadata) -> Metadata:
        try:
            lines = [self.wordMap[ind] for ind in charMetadata.lines]
            paragraphs = [self.wordMap[ind] for ind in charMetadata.paragraphs]
            sentences = [self.wordMap[ind] for ind in charMetadata.sentences]
            imagePositions = []
            return Metadata(paragraphs, lines, sentences, imagePositions)
        except KeyError as e:
            raise Exception("Error in forming word metadata: Key Error")
        except Exception as e:
            raise Exception("Error in forming word metadata")
class WordUtils:
    @staticmethod
    def extract_words(data: str) -> List[Word]:
        words = []
        start = 0
        cnt = 1
        try:
          for i in range(len(data)):
            if data[i] == " " or data[i] == "\n":
              if data[start:i] == " ":
                start = i + 1
                continue
              words.append(Word(data[start:i], start, i, cnt))
              start = i + 1
              cnt += 1
            # append the last word
          if data[start:] != " " and words[-1].start != start:
            words.append(Word(data[start:], start, len(data), cnt))
          return words
        except Exception as e:
          raise Exception("Error in extracting words")
    
    @staticmethod
    def indexToPos(words: List[Word], index: int) -> int:
        for word in words:
            if word.start <= index < word.end:
                return word.pos
        return -1
    
    def extract_words_metadata_from_char_metadata(words: List[Word], charMetadata: Metadata) -> Metadata:
        paragraphs = [WordUtils.indexToPos(words, charMetadata.paragraphs[0])]
        lines = [WordUtils.indexToPos(words, charMetadata.lines[0])]
        sentences = [WordUtils.indexToPos(words, charMetadata.sentences[0])]
        imagePositions = []
        return Metadata(paragraphs, lines, sentences, imagePositions)


    @staticmethod
    def extract_words_metadata(words: List[Word]) -> Metadata:
        paragraphs = [0]
        lines = [0]
        sentences = [0]
        imagePositions = []
        for word in words:
            if word.word == "\n":
                lines.append(word.pos)
            if word.word == ".":
                sentences.append(word.pos)
        return Metadata(paragraphs, lines, sentences, imagePositions)
    def extract_words_metadata_from_string(data: str) -> Metadata:
        return WordUtils.extract_words_metadata(WordUtils.extract_words(data))

def processPassage(passage: str, passageNo) -> Passage:
  header, data, source_details, questionNumbers, charMetadata, wordMetadata = "", "", "", "", Metadata([], [], [], []), Metadata([], [], [], [])
  section = 1 if passageNo <= 5 else 2
  try:
    header = extract_header(passage)
    data = extract_data(passage, header)
    questionNumbers = extract_question_numbers(header)
    source_details = extract_source_details(data)
    data = data.replace(source_details, "").strip()
    data = data.replace("\n\n", "\n")

    source_details = removenextline(source_details)
    header = removenextline(header)
    
    [data, charMetadata] = extract_character_metadata(data)
    wordMetadata = WordList(data).formWordMetadata(charMetadata)
  except Exception as e:
    print(f"Error in passage {passageNo}: {e}")
  return Passage(data, header, source_details, questionNumbers, section, charMetadata, wordMetadata)

def asPanadasDF(passages: List[Passage], paperNumber) -> pd.DataFrame:
    df = pd.DataFrame(columns=["Sample paper", "Section", "Question no","Passage", "Header", "Source details","Character Metadata","Word Metadata"])
    for i, passage in enumerate(passages):
        # if i > 4:
        #     passage.section = 2
        df = pd.concat([df, pd.DataFrame({
            "Sample paper": [paperNumber],
            "Section": [passage.section],
            "Question no": [passage.questionNumbers],
            "Passage": [passage.text],
            "Header": [passage.header],
            "Source details": [passage.source_details],
            "Character Metadata": [passage.characterMetadata.jsonize()],
            "Word Metadata": [passage.wordMetadata.jsonize()]
        })], ignore_index=True)
    return df

def saveAsExcel(passages: List[Passage], filename: str, paperNumber) -> None:
    df = asPanadasDF(passages, paperNumber)
    print(df)
    # write_text_to_file(df.to_string(), filename.replace("xlsx","txt"))
    # error here
    # df.to_excel(filename, index=False)
    writer = pd.ExcelWriter(filename, engine='xlsxwriter')
    df.to_excel(writer, index=False)
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']
    format_wrap = workbook.add_format({'text_wrap': True, 'valign': 'top'})
    for i in range(3):
        worksheet.set_column(i, i, 13, format_wrap)
    for i in range(3, len(df.columns)):
        worksheet.set_column(i, i, 60, format_wrap)
    writer.close()

if __name__ == '__main__':
    paperNumber = 1
    for paperNumber in range(1, 9):
        try:
            pdf_file_path = f"input/sat{paperNumber}QP_removed.pdf"
            pdf_text = extract_text_from_pdf(pdf_file_path)
            all_text = "".join(pdf_text)
            passages = PassageUtils.pre_process_passages(all_text)

            # print(len(passages))
            passageObjects = []
            for i, passage in enumerate(passages):
                # process passage
                passageObjects.append(processPassage(passage, i + 1))
                # print(passageObjects[-1])

            # print(len(passageObjects))
            # print(len(passages))
            write_text_to_file("****************************************\n\n\n".join(passages), "debug/SAT1tempPassages.txt")

            write_text_to_file("".join(pdf_text), "debug/SAT1temp.txt")
            saveAsExcel(passageObjects, f"output/SAT{paperNumber}Passages.xlsx", paperNumber)
        except Exception as e:
            print(f"Error in paper {paperNumber}: {e}")
            continue