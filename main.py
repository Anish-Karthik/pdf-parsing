from typing import List
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

@dataclass
class Passage:
  def __init__(self, text: str, questionNumbers: str,header: str, source_details: str,  images: List[str], paragraphs: List[int], 
        lines: List[int], sentences: List[int], 
        imagePositions: List[int], section: int):
    self.text = text
    self.questionNumbers = questionNumbers
    self.section = section
    self.header = header
    self.source_details = source_details
    self.images = images
    self.paragraphs = paragraphs
    self.lines = lines
    self.sentences = sentences
    self.imagePositions = imagePositions
  
  def __str__(self):
    return f"Text: {self.text}\nHeader: {self.header}\nSource Details: {self.source_details}\nImages: {self.images}\nParagraphs: {self.paragraphs}\nLines: {self.lines}\nSentences: {self.sentences}\nImage Positions: {self.imagePositions}"
  
  def __repr__(self):
    return f"Text: {self.text}\nHeader: {self.header}\nSource Details: {self.source_details}\nImages: {self.images}\nParagraphs: {self.paragraphs}\nLines: {self.lines}\nSentences: {self.sentences}\nImage Positions: {self.imagePositions}"
  
  def jsonize(self) -> str:
    return str({
      "text": self.text,
      "header": self.header,
      "source_details": self.source_details,
      "images": self.images,
      "paragraphs": self.paragraphs,
      "lines": self.lines,
      "sentences": self.sentences,
      "imagePositions": self.imagePositions
    })

  def jsonifyMetadata(self):
    return str({
      "header": self.header,
      "source_details": self.source_details,
      "images": self.images,
      "paragraphs": self.paragraphs,
      "lines": self.lines,
      "sentences": self.sentences,
      "imagePositions": self.imagePositions
    })

def processPassage(passage: str) -> Passage:
    try:
        # extract headers
        tmp = re.match(r"(Questions \d*-\d*(.|\n)*?(?=[A-Z]))",passage)
        # print(tmp.group())
        header = tmp.group()
        data = passage.replace(header,"").strip()

        tmp = re.findall(r"\d*-\d*", header)
        if tmp is None or len(tmp) == 0:
            questionNumbers = "No question numbers found"
        else:
            questionNumbers = tmp[0]

        # extract source details
        tmp = re.match(r"(((This passage is)|(Passage \d{1,})) (((?:.|\n)*?\.\n)|((?:.|\n)*?\.){3}))", data) # re.split(r"(?<=\n\n)(.|\n)*?(?=\n\n)",data)
        section = 1
        if tmp is None:
            source_details = "No source details found"
            section = 2
        else:
        # print("".join(tmp.groups()))
          source_details = tmp.group()  #"".join([x for x in tmp.groups() if x is not None])

        data = data.replace(source_details,"")

        data = data.replace("\n\n","\n")
        # indices of line breaks
        # paragraphs = re.findall(r"\n\n", data)

        lines = [0] + [m.end(0) for m in re.finditer(r"\n", data)]

        paragraphs = [0] + [m.end(0) for m in re.finditer(r"(\.|\?)\n", data)]

        sentences = [0] + [m.end(0) for m in re.finditer(r"\. ", data)]

        # Extract images
        # images = re.findall(r"Image \d{1,}", passage)
        # imagePositions = []
        # for image in images:
        #     imagePositions.append(passage.index(image))
        # # Extract paragraphs
        # paragraphs = re.findall(r"\n\n", passage)
        # # Extract lines
        # lines = re.findall(r"\n", passage)
        # # Extract sentences
        # sentences = re.findall(r"\. ", passage)
        return Passage(data, questionNumbers, header, source_details, [], paragraphs, lines, sentences, [], section)
    except Exception as e:
        print(f"Error in passage: {e}")
        return Passage(passage, "Error in passage", "Error in passage", "Error in passage", [], [], [], [], [], 0)

def asPanadasDF(passages: List[Passage], paperNumber) -> pd.DataFrame:
    df = pd.DataFrame(columns=["Sample paper", "Section", "Question no","Passage","Metadata"])
    for passage in passages:
        df = pd.concat([df, pd.DataFrame({
            "Sample paper": [paperNumber],
            "Section": [passage.section],
            "Question no": [passage.questionNumbers],
            "Passage": [passage.text],
            "Metadata": [passage.jsonifyMetadata()]
        })], ignore_index=True)
    return df

def saveAsExcel(passages: List[Passage], filename: str, paperNumber) -> None:
    df = asPanadasDF(passages, paperNumber)
    print(df)
    # write_text_to_file(df.to_string(), filename.replace("xlsx","txt"))
    # error here
    df.to_excel(filename, index=False)

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
            for passage in passages:
                # process passage
                passageObjects.append(processPassage(passage))
                # print(passageObjects[-1])

            # print(len(passageObjects))
            # print(len(passages))
            write_text_to_file("****************************************\n\n\n".join(passages), "debug/SAT1tempPassages.txt")

            write_text_to_file("".join(pdf_text), "debug/SAT1temp.txt")
            saveAsExcel(passageObjects, f"output/SAT{paperNumber}Passages.xlsx", paperNumber)
        except Exception as e:
            print(f"Error in paper {paperNumber}: {e}")
            continue