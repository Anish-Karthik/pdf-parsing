import json
import os


def get_context(passage_words, ind, step):
    ind += step
    words = ""

    cnt = 6
    while (ind >= 0 and ind < len(passage_words) and cnt > 0):
        if step == 1:
            words += passage_words[ind] + " "
        else:
            words = passage_words[ind] + " " + words
        ind += step
        cnt -= 1

    return words


# input_json_path = "correctedJsonSat/outputfinal/sat-sample-paper-1-passage2.json"
for input_json_path in sorted(os.listdir("sat/writing-comp-output")):

    input_json = json.loads(open(f"sat/writing-comp-output/{input_json_path}").read())

    passage = input_json["passage"]
    questions = input_json["questions"]
    passage_words = passage.split(" ")

    qns_reference = ["" for _ in range(len(questions))]
    modify_qns_list = list()

    for ind, word in enumerate(passage_words):

        if ("QS$$" in word and word[-1] not in modify_qns_list):
            modify_qns_list.append(word[-1])
            qns_reference[int(word[-1])] = get_context(passage_words, ind, -1)

        for modify_qn in modify_qns_list:
            if "$$" in word and word[-1] != modify_qn:
                continue
            qns_reference[int(modify_qn)] += word + " "

        if ("QE$$" in word and word[-1] in modify_qns_list):
            qns_reference[int(word[-1])] += get_context(passage_words, ind, 1)
            modify_qns_list.remove(word[-1])

    for i in qns_reference:
        print(i, end="\n\n\n")
    for ind, question in enumerate(input_json["questions"]):
        input_json["questions"][ind]["description"] += f".....{qns_reference[ind]}....."

    output_json = json.dumps(input_json, indent=4)
    with open(f"sat/writing-comp-output/{input_json_path}", "w") as f:
        f.write(output_json)
