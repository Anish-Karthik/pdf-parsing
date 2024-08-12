import fitz
import re
from typing import *
from model import *
import pytesseract
from PIL import Image
import io
import cv2


def is_qn_no(block):
    return re.search(r"(?<!.)\d+\.", block[4])


def is_option(block):
    return re.search(r"(?<!.\)\([A-E]\)", block[4])


def is_first_option(block):
    return re.search(r"(?<!.)\(A\)", block[4])


def is_option_match(ind, option_text):
    options = ["A", "B", "C", "D", "E"]
    return re.search(r"(?<!.)\(" + options[ind] + r"\)", option_text)


def is_last_option(block):
    return re.search(r"(?<!.)\(E\)", block[4])


def is_part_of_last_option(prev_line, line):
    diff = prev_line[3] - line[1]
    return diff >= 1 and diff < 3


def remove_next_line(text):
    return re.sub(r"\n", " ", text)


def remove_option_number(text):
    return re.sub(r"(?<!.)\([A-E]\)\s+ ?", "", text)


def remove_question_number(text):
    return re.sub(r"(?<!.)\d+\.\s+ ?", "", text)


def extract_question_number(text):
    qno = re.findall(r"(?<!.)(\d+)\.", text)
    return qno[0] if len(qno) > 0 else None


def get_underlined_text(doc, image, ind):

    img = doc.extract_image(image[0])
    pix = fitz.Pixmap(doc, image[0])
    image_bytes = pix.tobytes("png")
    image = Image.open(io.BytesIO(image_bytes))
    image.save("images/" + str(ind) + ".jpg")
    width, height = image.size

    top_half = image.crop((0, 0, width, height // 2))  # Crop the top half
    top_half.save("images/" + str(ind) + "half.jpg")

    bottom_half = image.crop((0, height * 0.6, width, height))
    bottom_half.save("images/" + str(ind) + "bottom_half.jpg")

    img = cv2.imread("images/" + str(ind) + "half.jpg")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    text = pytesseract.image_to_string(Image.fromarray(thresh), config='--psm 6')

    # print(text)

    img = cv2.imread("images/" + str(ind) + "bottom_half.jpg")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    Image.fromarray(thresh).save("images/" + str(ind) + 'cv2.jpg')

    bottom_text = pytesseract.image_to_string(Image.fromarray(thresh), config='--psm 6')

    # print(bottom_text)

    return re.sub(r"\n", "", text)


def replace_with_underlined_text(text, underlined_text):
    text = re.sub(r"(?<=\s)\n", underlined_text, text)
    return text


def insert_underlined_text(lines):
    new_lines = []
    for ind, line in enumerate(lines):
        if len(line) == 7:
            new_lines.append(line)
        else:
            if new_lines:
                new_lines[-1][4] = replace_with_underlined_text(new_lines[-1][4], line[4])
            else:
                lines[ind + 1][4] = replace_with_underlined_text(lines[ind + 1][4], line[4])
    return new_lines


def clean_block(str):
    str = str.replace("Passage", "\nPassage")
    str = str.replace("TIME—25 MINUTES 24 QUESTIONS ", "")
    return str


def fix_hyphens(str):
    splits = re.split(r"-\n", str)
    fixed_str = ""
    for ind, val in enumerate(splits):
        fixed_str += val

        if ind < len(splits) - 1:
            next_line = splits[ind + 1].split(" ", 1)
            if len(next_line) > 0:
                fixed_str += next_line[0]

            if len(next_line) > 1:
                splits[ind + 1] = "\n" + next_line[1]
            else:
                splits[ind + 1] = "\n"

    return fixed_str


def get_each_lines(doc):
    lines = []
    strip_first_word = False
    for page in doc:
        line = []
        blocks = page.get_text("blocks")
        border = 200
        stop_block = None
        for block in blocks:
            block = list(block)

            if strip_first_word:
                block[4] = " ".join(block[4].split()[1:])
                strip_first_word = False

            block[4] = clean_block(block[4])
            block[4] = fix_hyphens(block[4])

            if is_extra(block):
                continue

            if "STOP" in block[4]:
                stop_block = block
                continue
            if not re.search(r"^\.", block[4]):
                line.append(block)
            else:
                border = block[0]

        line = sorted(line, key=lambda x: (0 if x[0] < border else 1, x[1]))
        # extra property to check isLeft
        if stop_block:
            line.append(stop_block)
        line = [list(block) + [block[0] < border] for block in line]
        lines.extend(line)

    return lines


def get_options(lines):
    all_options = []
    for ind, line in enumerate(lines):
        text = ""
        if is_first_option(line):
            cur = ind
            while not is_last_option(lines[cur]):
                text += lines[cur][4]
                cur += 1
            text += lines[cur][4]
            cur += 1
            while is_part_of_last_option(lines[cur - 1], lines[cur]):
                text += lines[cur][4]
                cur += 1
            # print(text)
            options = re.split(r"(?<!.)[A-D]\)", text)
            options = [remove_next_line(option) for option in options]
            all_options.append(options[1:5])
    return all_options


def is_extra(block) -> bool:
    # isNum = bool(re.match(r"\d+\n",block[4]))
    # if not alphanumeric
    return (
        re.search(r"Line\n5?", block[4]) or
        re.search(r"Unauthorized copying", block[4]) or
        re.search(r"READING COMPREHENSION", block[4]) or
        re.search(r"SAT.*PRACTICE\n", block[4]) or
        re.search(r"NEXT PAGE", block[4]) or
        re.search(r"CRITICAL READING", block[4]) or
        re.search(r"SELF-ASSESSMENT TEST", block[4]) or
        (re.search(r"TIME", block[4]) and re.search(r"MINUTES", block[4])) or
        re.search(r".com", block[4])
    ) and len(block[4]) < 50


def get_questions_alter(lines) -> List[Question]:
    all_questions: List[Question] = []
    options: List[Option] = []
    # all_options:List[Option]  = []
    cur_op = 0
    op_text = ""
    op_0_ind = None
    options_started = False
    lines.append([0, lines[-1][3] + 5, 0, 0, "", 0, 0, False])
    for ind, line in enumerate(lines):
        for content in line[4].split("\n"):

            if cur_op == 4 and not is_part_of_last_option(lines[ind - 1], line):
                options.append(Option(remove_option_number(op_text)))
                if op_0_ind is not None:
                    qn_no, qn_text = get_question(lines, op_0_ind)
                    all_questions.append(Question(qn_no, qn_text, options))
                    options_started = False
                options = []
                op_0_ind = None
                cur_op = 0

            if (cur_op < 4 and is_option_match(cur_op + 1, content)):
                cur_op += 1
                options.append(Option(remove_option_number(op_text)))

            if is_option_match(cur_op, content):
                # print(content)
                if cur_op == 0:
                    op_0_ind = ind
                options_started = True
                op_text = ""

            if options_started:
                op_text += remove_next_line(content)

        # print(options_started,line[4])
    return all_questions


def get_question(lines, ind):
    qn_text = ""
    cur = ind
    while cur >= 0:
        if not is_extra(lines[cur]):
            qn_text = lines[cur][4] + qn_text

        if is_qn_no(lines[cur]):
            qn_no = extract_question_number(lines[cur][4])
            return remove_next_line(qn_no), remove_next_line(remove_question_number(qn_text.split("(A)", 1)[0]))

        cur -= 1
    return "", ""


# def populate_reference()
# [[qtext, qno]]
def populate_referencesV1(input_list: List[Question]):
    all_items = input_list
    pattern = r"lines*\s*(\d+)(?:\s*(?:,|-|and)\s*(\d+))?"

    for ind, item in enumerate(all_items):
        reference_lines_match = re.findall(pattern, item.description if isinstance(item, list) else item, re.IGNORECASE)
        reference_lines = []
        for ref_line in reference_lines_match:
            reference_lines.append(list(ref_line))

        if isinstance(item, list):
            all_items[ind].append(reference_lines)
        else:
            all_items[ind] = [all_items[ind], reference_lines]

    return all_items


'''
FINAL OUTPUT:
QUESTIONS: [
]

'''
