from classes.metadata import Metadata
from utils.word import WordUtils
from collections import defaultdict
from typing import List, Tuple

class WordList:
    def __init__(self, data: str):
        self.words = WordUtils.extract_words(data)
        self.wordMap = {}
        self.revWordMap = defaultdict(lambda: -1)
        self.data = data
        for word in self.words:
            self.wordMap[word.start] = word.pos
            self.revWordMap[word.end] = word.pos

    def formWordMetadata(self, charMetadata: Metadata) -> Metadata:
        try:
            lines = [self.wordMap[ind] for ind in charMetadata.lines]
            paragraphs = [self.wordMap[ind] for ind in charMetadata.paragraphs]
            sentences = [self.wordMap[ind] for ind in charMetadata.sentences]
            # TODO need debugging here
            # starting the word from the word instead of number
            underlines = self.getUnderlines(charMetadata.underlines)
            imagePositions = []
            return Metadata(paragraphs, lines, sentences, imagePositions, underlines)
        except KeyError as e:
            raise Exception("Error in forming word metadata: Key Error")
        except Exception as e:
            raise Exception("Error in forming word metadata")
        
    def getUnderlines(self, underlineSentences: List[Tuple[int,int]]) -> List[Tuple[int,int]]:
        underlines = []
        for underline in underlineSentences:
            st = underline[0]
            start = -1
            if st in self.wordMap:
                start = self.wordMap[st]
            elif st+2 in self.wordMap:
                start = self.wordMap[st+2]
            elif st+3 in self.wordMap:
                start = self.wordMap[st+3]
            else:
                print(f"Could not find start of underline: {st}")
            end = self.revWordMap[underline[1]]
            underlines.append((start, end))
        return underlines