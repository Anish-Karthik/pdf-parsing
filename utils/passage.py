import re
from typing import Tuple, List

from classes.metadata import Metadata
from classes.passage import Passage
from classes.wordlist import WordList
from utils.util import removenextline
from utils.underline import Underline

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
  qnos = []
  st, en = -1, 0
  try:
    st,en = map(int, tmp[0].split("-"))
  except:
    if st == -1 and en == -1:
      return "No question numbers found"
    if en == -1:
      en = st + 10
    if st == -1:
      st = en - 10
  for i in range(st, en+1):
    qnos.append(str(i))
  return ",".join(qnos)

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
  data = re.sub(r"(\.|\?) ?\n", r"\1\n\t", data)
  # data = strip_excess_whitespace_paragraphs(data)
  # match all the \n except the \n following the pattern Passage \d*
  # data = re.sub(r"(?<!Passage \d*)\n", "", data)
  
  lines = [0] + [m.end(0) for m in re.finditer(r"(?<!Passage \d)\n", data)]
  paragraphs = [0] + [m.end(0)-1 for m in re.finditer(r"(\.|\?)\n\t", data)]
  # replace all the \n with " ", which are not followed by \t
  data = re.sub(r"\n(?!\t)", r" ", data)
  sentences = [0] + [m.end(0) for m in re.finditer(r"\. ", data)]
  return data, Metadata(paragraphs, lines, sentences, [])

def processPassage(passage: str, passageNo, underlineObject: Underline = None) -> Passage:
  header, data, source_details, questionNumbers, charMetadata, wordMetadata = "", "", "", "", Metadata([], [], [], []), Metadata([], [], [], [])
  section = 1 if passageNo <= 5 else 2
  try:
    header = extract_header(passage)
    data = extract_data(passage, header)
    questionNumbers = extract_question_numbers(header)
    source_details = extract_source_details(data)
    data = data.replace(source_details, "").strip()
    data = data.replace("\n\n", "\n")
    if underlineObject is not None:
      underlineObject.add_reference_number_to_underline(data)

    source_details = removenextline(source_details)
    header = removenextline(header)

    [data, charMetadata] = extract_character_metadata(data)
    if underlineObject is not None:
      charMetadata.underlines = underlineObject.map_metadata_to_underlines(data)
    
    wordMetadata = WordList(data).formWordMetadata(charMetadata)
  except Exception as e:
    print(f"Error in passage {passageNo}: {e}")
  return Passage(data, header, source_details, questionNumbers, section, charMetadata, wordMetadata)