class Word:
    def __init__(self, word: str, start: int, end: int, pos: int):
        self.word = word
        self.start = start
        self.end = end
        self.pos = pos # denoting the position of the word in the data

    @staticmethod
    def from_string(word: str, start: int, pos: int):
        return Word(word, start, start + len(word), pos)