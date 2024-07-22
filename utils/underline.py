import re
from typing import List, Tuple

from parser import get_all_underlined_sentences_only,get_all_underlined_sentences

class Underline:
  def __init__(self, all_underline_sentences:List[Tuple[str, str]] = []) -> None:
    self.all_underline_sentences = []
    self.current = 0
  
  def read_all_underline_sentences(self, pdf_path):
    self.all_underline_sentences = get_all_underlined_sentences_only(get_all_underlined_sentences(pdf_path))
    self.current = 0
    return self.all_underline_sentences
  
  def add_reference_number_to_underline(self, data: str):
    try:
      breakNow = False
      cnt = 1
      underlines = []
      inc = 0
      i = self.current
      passage = data.replace("\n", " ") 
      while not breakNow and i < len(self.all_underline_sentences):
        [sentence, qn_no] = self.all_underline_sentences[i]
        if "red." in sentence:
          print(sentence)
        special_chars = ["(", ")", "[", "]", "{", "}", ".", "*", "+", "?", "^", "$", "|", "\\"]
        for char in special_chars:
          if char in sentence:
            sentence = sentence.replace(char, "\\" + char)
        tmp = re.search(r"\d\n? ?" + sentence, passage)
        if tmp is not None:
          underlines.append((tmp.start(), tmp.end()))
          pass
        else:
          tmp = [m for m in re.finditer(sentence, passage)]
          matchIs = None
          if len(tmp) == 1:
            matchIs = tmp[0]
          elif len(tmp) == 0:
            if i != self.current:
              print("Could not find underlined sentence: " + sentence)
            breakNow = True
          else:
            if len(underlines) == 0:
              matchIs = tmp[0]
            else:
              for i in range(1, len(tmp)):
                if tmp[i].start() > underlines[-1][1]:
                  matchIs = tmp[i]
                  break
              else:
                matchIs = None
          if matchIs is None:
            breakNow = True
          else:
            passage = passage.replace(sentence, str(cnt)+" "+sentence)
            cnt+=1
            continue
        i += 1
    except Exception as e:
      print(f"Error in adding reference number to underline: {e}")
      raise Exception("Error in adding reference number to underline")

  def map_metadata_to_underlines(self, passage: str) -> List[int]:
    underlines = []
    # find the index of the underlined sentence in the passage matching the regex pattern
    breakNow = False
    i = self.current
    while not breakNow and i < len(self.all_underline_sentences):
      [sentence, qn_no] = self.all_underline_sentences[i]
      tmp = re.search(r"\d\n? ?" + sentence, passage)
      if tmp is not None:
        underlines.append((tmp.start(), tmp.end()))
      if sentence not in passage:
        breakNow = True
      if breakNow and i == self.current:
        break
      i += 1
    self.current = i
    return underlines