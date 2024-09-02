import re
def removenextline(text: str) -> str:
    return re.sub(r"\n"," ",text)
def write_text_to_file(text: str, file_path: str) -> None:
    with open(file_path, "w", encoding="UTF-8") as f:
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

def isStartOfPassageHeaderBaron(block):
    return (
        re.match(r'^A Natural Synthetic ', block[4]) 
        or re.match(r'^The Slums ', block[4])
        or re.match(r'^Microbiomes ', block[4])
        or re.match(r'^Hemoglobin ', block[4])
        or re.match(r'^Time Travel ', block[4])
        or re.match(r'^The Downfall of Democracy\? ', block[4])
        or re.search(r'Ain’t I a Woman\? ', block[4].replace('\u2019','’'))
        or re.search(r'Ohio. \(As a historical text, this uses antiquated language.\)', block[4])
        or re.search(r'Chapman Catt', block[4])
        or re.match(r'^Earthquakes $', block[4])
        or re.search(r'^Buyer\u2019s Remorse: ', block[4])
        or re.match(r'^The Value of Engineering ', block[4])
        or re.match(r'^Chemistry of Cooking ', block[4])
        or re.search(r'^Is It the Heart or the Brain\? ', block[4])
        or re.match(r'^Sages and Fools ', block[4])
        or re.match(r'Surfactants', block[4])
        or re.match(r'^Alternative Splicing ', block[4])
        or re.search(r'^The Woes of Consumerism ', block[4])
        or re.match(r'^Alternative Energy', block[4])
        or re.match(r'^What\u2019s Not to \u201cLike\u201d', block[4])
        or re.match(r'^Searching the Skies ', block[4])
        or re.match(r'^Finnegan\u2014A short story ', block[4])
        or re.match(r'^A Democratic Duel ', block[4])
        or re.match(r'^Humanity\u2019s Code ', block[4])
        or re.match(r'^Influenza ', block[4])

        or re.match(r'^Charles Dickens’s ', block[4])
        or re.match(r'cared for by his sister', block[4])
        or re.match(r'of his affections while simultaneously', block[4])
        # or re.match(r'The first is a speech', block[4])
        or re.match(r'The following passage is from', block[4])
        or re.match(r'Two contemporary writers', block[4])
        or re.match(r'Two scientists', block[4])
        or re.match(r'Two passages', block[4])
        or 'adapted from' in block[4].lower()
        or re.match(r'The following is an excerpt from', block[4])
        or re.match(r'Price, returns home after', block[4])
        or re.match(r'Below is', block[4])
        or re.match(r'the chapter is', block[4])
        or re.match(r'which he muses about', block[4])
        or re.search(r'in 18\d\d', block[4], re.IGNORECASE)
        or re.search(r'economic recovery\.1', block[4])
        or re.search(r'Russia 1917\.', block[4])
        or re.search(r'Thornfield Hall, is engaged', block[4])
        or re.search(r'unexpected events to him that have recently occurred', block[4])

        or re.search(r'Dedalus, Joyce', block[4])
        or re.search(r'Below he contemplates the diverging paths before him after a priest warns', block[4])
        or re.search(r'his intended holy position', block[4])

        or re.search(r'MEDITATION I.', block[4])
        or re.search(r'Of the Things of Which We May Now Doubt', block[4])

        or re.match(r'^. Y ', block[4])
        or re.match(r'oung, \u201cPathogenesis of Hemoglobinopathies', block[4])

        or re.match(r'American wilderness. He would later be called the godfather of the American environmental', block[4])
        or re.match(r'^movement. $', block[4])

        or re.match(r'^Civilization\u201d at the Smithsonian',block[4])

        or re.search(r'1895. The second is part of a 1903 response, titled \u201cOf Mr. Booker T. Washington', block[4])
        or re.search(r'W\.E\.B\. DuBois\. \(As historical texts, these use antiquated language\.\)', block[4])

        # or re.match(r'Below are \d+', block[4])
        or re.search(r'The future of this', block[4])
        or re.match(r'An English professor', block[4]) # has subheading
        or re.search(r'excerpt ', block[4])
        or re.search(r'Fitzgerald', block[4])
        or re.search(r'protagonist, Amory Blaine.', block[4])
        or re.search(r'Dwight D. Eisenhower', block[4])
    )