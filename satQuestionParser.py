import fitz
import re
from typing import *
from model import *
import pytesseract
# from PIL import Image
import io
import cv2
import json


def is_qn_no(block):
    if re.search(r"^\d+\.\s+", block[4]):
        # print(block[4])
        return True
    return False


def is_option(block):
    return re.search(r"(?<!.)[A-D]\)", block[4])


def is_first_option(block):
    return re.search(r"(?<!.)A\)", block[4])


def is_option_match(ind, option_text):
    options = ["A", "B", "C", "D"]
    return re.search(r"(?<!.)\(" + options[ind] + r"\)", option_text)


def is_last_option(block):
    return re.search(r"(?<!.)D\)", block[4])


def is_part_of_last_option(prev_line, line):
    diff = prev_line[3] - line[1]
    return (diff >= -1 and
            diff < 3 and
            not re.match(r"^\d+.", line[4]))


def remove_next_line(text):
    return re.sub(r"\n", " ", text)


def remove_option_number(text):
    return re.sub(r"(?<!.)\([A-D]\)\s+", "", text)


def remove_question_number(text):
    return re.sub(r"(?<!.)\d+\.\s+", "", text)


def extract_question_number(text):
    qno = re.findall(r"(?<!.)(\d+)\.\s+", text)
    return qno[0] if len(qno) > 0 else None


# def get_underlined_text(doc, image, ind):

#     img = doc.extract_image(image[0])
#     pix = fitz.Pixmap(doc, image[0])
#     image_bytes = pix.tobytes("png")
#     image = Image.open(io.BytesIO(image_bytes))
#     image.save("images/" + str(ind) + ".jpg")
#     width, height = image.size

#     top_half = image.crop((0, 0, width, height // 2))  # Crop the top half
#     top_half.save("images/" + str(ind) + "half.jpg")

#     bottom_half = image.crop((0, height * 0.6, width, height))
#     bottom_half.save("images/" + str(ind) + "bottom_half.jpg")

#     img = cv2.imread("images/" + str(ind) + "half.jpg")
#     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#     thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
#     text = pytesseract.image_to_string(Image.fromarray(thresh), config='--psm 6')

#     # print(text)

#     img = cv2.imread("images/" + str(ind) + "bottom_half.jpg")
#     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#     blur = cv2.GaussianBlur(gray, (5, 5), 0)
#     thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

#     Image.fromarray(thresh).save("images/" + str(ind) + 'cv2.jpg')

#     bottom_text = pytesseract.image_to_string(Image.fromarray(thresh), config='--psm 6')

#     # print(bottom_text)

#     return re.sub(r"\n", "", text)


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


def is_multi_block(block):
    if re.search(r"\d\.", block[4]) and re.search(r"\([A-D]\)", block[4]):
        return True
    all_matches = re.findall(r"\([A-D]\)", block[4])
    if len(all_matches) > 1:
        return True
    return False


def split_multi_block(block):
    text = block[4]
    # print("INPUT:",text)
    output = split_line1(text)
    # print("OUTPUT:","\n".join(output), end="\n\n")
    output_text = [item for item in output if item]

    output_blocks = []
    for text in output_text:
        output_blocks.append([block[0], block[1], block[2], block[3], text, block[5], block[6]])

    # print(output_blocks)
    return output_blocks


def processBlock(block):
    # if block starts (/d+) then block[0] = 39.5645751953125
    if re.search(r"^\(\d+\)", block[4]) or re.search(r"^Line\s+", block[4]):
        block = list(block)
        block[0] = 39.5645751953125
        # block[4] = re.sub(r"^\(\d+\)", "", block[4])
        block[4] = re.sub(r"^Line\s+", "", block[4])
    return block


def get_each_lines(doc):
    lines = []
    hasAnswersStarted = False
    skip = False
    for page in doc[13:]:
        # images = page.get_images()

        pg_lines = []
        # for img_index, img in enumerate(images):
        #     xref = img[0]
        #     img_rect = page.get_image_rects(xref)[0]

        #     if abs(img_rect.y0 - img_rect.y1) < 50:  # is text image
        #         text = get_underlined_text(doc, img, img_index)
        #         coords = (img_rect.x0, img_rect.y0, img_rect.x1, img_rect.y1, text)

        #         pg_lines.append(coords)

        blocks = page.get_text("blocks")
        border = 323
        for block in blocks:
            block = list(block)
            # print(block)
            if "STEP-BY-STEP PRACTICE" in block[4]:
                skip = True
                continue
            if skip:
                if "PRACTICE EXERCISES" in block[4]:
                    skip = False
                continue
            if "ANSWERS EXPLAINED" in block[4]:
                skip = False
                hasAnswersStarted = True
                print("Answer started Split")
            if not re.search(r"(?<!.)\.{5,}", block[4]):
                # print(block)
                block = processBlock(block)
                # if is_multi_block(block):
                # print("\n\n\n\n\n")
                if hasAnswersStarted:
                    pg_lines.append([*block[:4], block[4].strip() + " ", *block[5:]])
                    continue
                split_blocks = split_multi_block(block)
                # print(split_blocks)
                # print("\n\n\n\n\n")
                pg_lines.extend([[*b[:4], b[4].strip() + " ", *b[5:]] for b in split_blocks])
                # else:
                #     pg_lines.append(block)

            else:
                border = block[0]
        pg_lines = sorted(pg_lines, key=lambda x: (x[3], x[0]))

        # pg_lines = insert_underlined_text(pg_lines)

        # extra property to check isLeft
        pg_lines = [list(block) + [block[0] < border] for block in pg_lines]

        # for line in pg_lines:
        #     print(line)

        lines.extend(pg_lines)
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
        re.search(r"CO NTI N U E", block[4]) or
        re.search(r"STOP", block[4]) or
        re.search(r"SAT.*PRACTICE\n", block[4])
    )


def split_line1(text):
    res_lines = []
    lines = re.split(r"\n|(\([A-D]\))|(\b\d{1,2}\.\s+)", text)
    # print(lines)
    # ["sdsd","(A)", None, "asda"]
    res_lines = [lines.pop(0)]
    for i in range(0, len(lines), 3):
        if i + 1 < len(lines):
            res_lines.append((lines[i] if lines[i] else "") + (lines[i + 1] if lines[i + 1] else "") + lines[i + 2])
    res_lines = [line for line in res_lines if line or line != ""]
    return res_lines


def clean_text(text):
    text = text.strip()
    text = re.sub(r"\n+", "\n", text)
    text = re.sub(r" +", " ", text)
    text = re.sub(r"\n +", "\n", text)
    text = re.sub(r" +\n", "\n", text)
    text = re.sub(r"\. +", ". ", text)
    text = re.sub(r" +\.", ".", text)
    text = re.sub(r"\.\.\.", " ...", text)
    return text


def get_questions_alter(lines) -> List[Question]:
    all_questions: List[Question] = []
    options: List[Option] = []
    # all_options:List[Option]  = []
    cur_op = 0
    op_text = ""
    op_0_ind = None
    options_started = False
    import json
    lines.append([0, lines[-1][3] + 5, 0, 0, "", 0, 0, False])
    for ind, line in enumerate(lines):
        # newContents = split_line1(line[4])
        # print(line)
        # for content in newContents:
        #     print(content)
        # # print("*newContents", newContents)
        #     # print(line[4])
        if cur_op == 3 and not is_part_of_last_option(lines[ind - 1], line):
            options.append(Option(clean_text(remove_option_number(op_text))))
            if op_0_ind:
                qn_no, qn_text = get_question(lines, op_0_ind)
                # print(qn_no, qn_text)
                all_questions.append(Question(qn_no, clean_text(qn_text), options))
                # print(json.dumps(all_questions[-1].to_json(), indent=4))
                options_started = False
            options = []
            op_0_ind = None
            cur_op = 0

        if (cur_op < 3 and is_option_match(cur_op + 1, line[4])):
            cur_op += 1
            options.append(Option(clean_text(remove_option_number(op_text))))

        if is_option_match(cur_op, line[4]):
            # print(line[4])
            if cur_op == 0:
                op_0_ind = ind
            options_started = True
            op_text = ""

        if options_started:
            op_text += remove_next_line(line[4])

        # print(options_started,line[4])
    # print(all_questions)  using json

    import json
    # print(json.dumps([question.to_json() for question in all_questions], indent=4))
    return all_questions


def get_question(lines, ind):
    qn_text = ""
    cur = ind - 1
    while cur >= 0:
        if not is_extra(lines[cur]):
            qn_text = lines[cur][4] + " " + qn_text

        if is_qn_no(lines[cur]):
            qn_no = extract_question_number(lines[cur][4])
            return remove_next_line(qn_no), remove_next_line(remove_question_number(qn_text)).replace(r"\s+", " ")
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
