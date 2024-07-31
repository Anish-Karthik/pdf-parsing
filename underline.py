import fitz
import re
from model import *


def calculate_overlap(line, word):

    line_x1 = line[1].x
    line_x2 = line[2].x
    word_x1 = word[0]
    word_x2 = word[2]

    overlap = max(0, min(line_x2, word_x2) - max(line_x1, word_x1))

    word_len = word_x2 - word_x1

    return overlap / word_len


def eligible_item(item):
    return item[0] == "l" and item[1].y == item[2].y


def is_underlined(word, drawn_lines):
    for line in drawn_lines:
        if line[1].y > word[1] and line[1].y - word[1] < 13:
            if calculate_overlap(line, word) > 0.9:
                return True
    return False


def get_lines(page):
    drawn_lines = []
    blocks = page.get_drawings()

    for block in blocks:
        for item in block["items"]:
            if eligible_item(item):
                drawn_lines.append(item)

    return drawn_lines


def get_all_words(doc):
    all_words = []
    for pgno, page in enumerate(doc):
        words = page.get_text("words")
        for word in words:
            word = tuple(list(word) + [pgno])
            all_words.append(word)
    return all_words


def get_words_from_passage(passage_words: List, words) -> List:
    start_p = 0
    start = 0
    match_words = []
    while start_p < len(passage_words) and start < len(words):
        max_match = 0
        max_match_start = start

        if passage_words[start_p] != words[start][4]:
            start += 1
            continue

        for i in range(start, len(words)):
            match = 0
            match_start = i
            while start_p + match < len(passage_words) and i < len(words) and passage_words[start_p + match] == words[i][4]:
                match += 1
            if match > max_match:
                max_match = match
                max_match_start = match_start

        for i in range(max_match_start, max_match_start + max_match):
            match_words.append(words[i])
            # print(words[i])

        start = max_match_start + max_match
        start_p += max_match

    return match_words


def passage_to_words(passage) -> List[str]:
    passage = re.sub(r"\t", " ", (re.sub(r"\n", " ", passage)))
    passage = [w for w in passage.split(" ") if len(w) > 0 and w != " "]
    # for w in passage:
    #     print(w)
    return passage


def underlined_references(comprehension: ReadingComprehension, doc) -> ReadingComprehension:
    # passage = comprehension.passage.passage
    # passage = re.sub(r"\t", "", (re.sub(r"\n", " ", passage)))
    passage = passage_to_words(comprehension.passage.passage)
    all_words = get_all_words(doc)
    # print(passage)
    words = get_words_from_passage(passage, all_words)
    # print("\n\n\n\n")

    drawn_lines = []
    for page in doc:
        drawn_lines.append(get_lines(page))

    references: List[Reference] = []
    prev_word_is_underlined = False
    start_word = 0
    end_word = 0
    qn_no = 0

    for ind, w in enumerate(words):
        if is_underlined(w, drawn_lines[w[8]]):
            if not prev_word_is_underlined:
                # print()
                maybe_qn_no = all_words[all_words.index(w) - 1]
                if re.match(r'\d+', maybe_qn_no[4]):
                    qn_no = maybe_qn_no[4]
                else:
                    qn_no = 0
                start_word = ind
            # print(w[4],end=" ")
            prev_word_is_underlined = True
        else:
            if prev_word_is_underlined:
                end_word = ind - 1
                if qn_no != 0:
                    for qn in comprehension.questions:
                        if qn.qno == qn_no:
                            qn.references.append(Reference(start_word, end_word))
                            
                            print(f"start_word:{start_word} end_word:{end_word} qn_no:{qn_no}")
                            break

            prev_word_is_underlined = False

    # print("\n\n\n\n")

    # for ref in references:
    #     print(ref.start_word,ref.end_word)
    # print(len(references))
    return comprehension

# def underlined_text(pdf_path):

#     doc = fitz.open(pdf_path)

#     underlined_sentences_all_pages = []

#     for pgno,page in enumerate(doc):
#         underlined_sentences = []
#         underlined_sentence = []
#         drawn_lines = get_lines(page)
#         words = page.get_text("words")

#         if pgno>10:

#             prev_word_is_underlined = False
#             qn_no=""
#             for ind,w in enumerate(words):
#                 # print(w)
#                 if is_underlined(w,drawn_lines):
#                     if not prev_word_is_underlined:
#                         if underlined_sentence != []:
#                             underlined_sentences.append([underlined_sentence,qn_no])
#                         underlined_sentence = []

#                         qn_no = words[ind-1][4] if re.match(r'^\d+',words[ind-1][4]) else ""
#                         # print("\n")


#                     underlined_sentence.append(w)
#                     # print(w[4],end =" ")
#                     prev_word_is_underlined = True
#                 else:
#                     prev_word_is_underlined = False
#             if len(underlined_sentence):
#                 underlined_sentences.append([underlined_sentence,qn_no])

#         underlined_sentences_all_pages.append(underlined_sentences)

#     return underlined_sentences_all_pages

pdf_path = "/Users/pranav/Downloads/SAT Practice Test 1 12.22.54 PM.pdf"

doc = fitz.open(pdf_path)


# for underlined_sentences in underlined_sentences_all_pages:
#     for sentence in underlined_sentences:
#         qn_no = sentence[1]
#         underlined_sentence = sentence[0]
#         print(qn_no, end=" ")
#         for w in underlined_sentence:
#             print(w[4], end=" ")
#         print()
#     print()
