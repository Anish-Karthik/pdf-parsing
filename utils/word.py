from typing import List
from classes.word import Word
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
          raise Exception(f"Error in extracting words: {e}")