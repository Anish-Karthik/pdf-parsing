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