import re
def removenextline(text: str) -> str:
    return re.sub(r"\n"," ",text)
def write_text_to_file(text: str, file_path: str) -> None:
    with open(file_path, "w+", encoding="UTF-8") as f:
        f.write(text)


def calculate_overlap(line, word):
    line_x1 = line[1].x
    line_x2 = line[2].x
    word_x1 = word[0]
    word_x2 = word[2]

    overlap = max(0, min(line_x2, word_x2) - max(line_x1, word_x1))

    word_len = word_x2 - word_x1

    return overlap/word_len


def eligible_item(item):
    return item[0] == "l" and item[1].y == item[2].y

def is_underlined(word,drawn_lines):
    for line in drawn_lines:
        if line[1].y > word[1] and line[1].y - word[1]<13  :
            return calculate_overlap(line, word) > 0.9
            
def get_lines(page):
    drawn_lines = []
    blocks = page.get_drawings()

    for block in blocks:
        for item in block["items"]:
            if eligible_item(item):
                drawn_lines.append(item)

    return drawn_lines

