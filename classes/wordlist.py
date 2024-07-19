from utils.word import WordUtils
from classes.metadata import Metadata

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
