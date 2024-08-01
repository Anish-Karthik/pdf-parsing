import fitz
import re
from typing import *
from model import *


def is_qn_no(block):
    return re.search(r"(?<!.)\d+( ){0,1}\n", block[4])


def is_option(block):
    return re.search(r"(?<!.)[A-D]\)", block[4])


def is_first_option(block):
    return re.search(r"(?<!.)A\)", block[4])


def is_option_match(ind, block):
    options = ["A", "B", "C", "D"]
    return re.search(r"(?<!.)" + options[ind] + r"\)", block[4])


def is_last_option(block):
    return re.search(r"(?<!.)D\)", block[4])


def is_part_of_last_option(prev_line, line):
    diff = prev_line[3] - line[1]
    return diff >= 1 and diff < 3


def remove_next_line(text):
    return re.sub(r"\n", " ", text)


def remove_option_number(text):
    return re.sub(r"(?<!.)[A-D]\) ?", "", text)


def get_each_lines(doc, isAnswer=False):
    lines = []
    for page in doc:
        line = []
        blocks = page.get_text("blocks")
        border = 323
        for block in blocks:
            block = list(block)
            # if isAnswer:
            #     line.append(block)
            #     continue
            if not re.search(r"^\.", block[4]):
                line.append(block)
            else:
                border = block[0]
        line = sorted(line, key=lambda x: (0 if x[0] < border else 1, x[1]))
        # extra property to check isLeft
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
        re.search(r"CO NTI N U E", block[4]) or
        re.search(r"STOP", block[4]) or
        re.search(r"SAT.*PRACTICE\n", block[4])
    )


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
        if cur_op == 3 and not is_part_of_last_option(lines[ind - 1], line):
            if op_0_ind is not None:
                options.append(Option(remove_option_number(op_text)))
                qn_no, qn_text = get_question(lines, op_0_ind)
                all_questions.append(Question(qn_no.strip(), qn_text, options))
            options_started = False
            options = []
            op_0_ind = None
            cur_op = 0

        if (cur_op < 3 and is_option_match(cur_op + 1, line)):
            cur_op += 1
            options.append(Option(remove_option_number(op_text)))

        if is_option_match(cur_op, line):
            if cur_op == 0:
                op_0_ind = ind
            options_started = True
            op_text = ""

        if options_started:
            op_text += remove_next_line(line[4])

        # print(options_started,line[4])
    return all_questions


def get_question(lines, ind):
    # return lines[ind-1][4]
    # for line in lines:
    # print(line)
    qn_text = ""
    cur = ind - 1
    while not is_qn_no(lines[cur]):
        if not is_extra(lines[cur]):
            qn_text = lines[cur][4] + qn_text
        cur -= 1
    qn_no = lines[cur][4]
    return remove_next_line(qn_no), remove_next_line(qn_text)


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
