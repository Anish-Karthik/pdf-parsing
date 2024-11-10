import json


input_file_path = "/home/barath/Documents/Neet/quizzes.json"


def first_and_last_chars(string):
    words = string.split()
    first_word = words[0]
    last_word = words[-1]
    return first_word[0].upper() + last_word[0].lower()


def assign_short_characters(topics):
    biology_index = 0
    physics_index = 0

    biologySymbols = [
        "🧬",  # DNA double helix
        "🧪",  # Test tube
        "🧫",  # Petri dish
        "🔬",  # Microscope
        "🌱",  # Seedling
        "🌿",  # Herb
        "🌾",  # Sheaf of rice
        "🍃",  # Leaf fluttering in wind
        "🌸",  # Blossom
        "🌼",  # Blossom
        "🍀",  # Four leaf clover
        "🌳",  # Deciduous tree
        "🌴",  # Palm tree
        "🌍",  # Earth globe
        "🐾",  # Paw prints
        "🐢",  # Turtle
        "🐉",  # Dragon
        "🐠",  # Tropical fish
        "🦋",  # Butterfly
        "🐦",  # Bird
        "🦜",  # Parrot
        "🐋",  # Whale
        "🐘",  # Elephant
        "🦒",  # Giraffe
        "🦙",  # Llama
        "🍄",  # Mushroom
        "🌾",  # Ear of rice
        "🪴"  # Potted plant
    ]

    physicsSymbols = [
        "α",  # Alpha
        "β",  # Beta
        "γ",  # Gamma
        "δ",  # Delta
        "ε",  # Epsilon
        "ζ",  # Zeta
        "η",  # Eta
        "θ",  # Theta
        "ι",  # Iota
        "κ",  # Kappa
        "λ",  # Lambda
        "μ",  # Mu
        "ν",  # Nu
        "ξ",  # Xi
        "ο",  # Omicron
        "π",  # Pi
        "ρ",  # Rho
        "σ",  # Sigma
        "τ",  # Tau
        "υ",  # Upsilon
        "φ",  # Phi
        "χ",  # Chi
        "ψ",  # Psi
        "ω",  # Omega
        "ℵ",  # Aleph
        "ℤ",  # Set of integers
        "ℝ"  # Set of real numbers
    ]

    for topic in topics:
        if (topic["subject"] == "Biology"):
            topic["symbol"] = biologySymbols[biology_index]
            biology_index += 1
        if (topic["subject"] == "Physics"):
            topic["symbol"] = physicsSymbols[physics_index]
            physics_index += 1
        if (topic["subject"] == "Chemistry"):
            topic["symbol"] = first_and_last_chars(topic["topic"])
        if (topic["subject"] == "All"):
            topic["symbol"] = "Re"


def assign_cell():

    p_topics = []
    c_topics = []
    b_topics = []
    r_topics = []

    topics = sorted(topics, key=lambda x: x["quiz_id"])

    for topic in topics:
        if topic["subject"] == "Biology":
            b_topics.append(topic)
        elif topic["subject"] == "Chemistry":
            c_topics.append(topic)
        elif topic["subject"] == "Physics":
            p_topics.append(topic)
        else:
            r_topics.append(topic)

    cell_id = 1
    for t in p_topics:
        t["cell"] = cell_id
        cell_id += 1

    cell_id = 28
    for t in c_topics:
        t["cell"] = cell_id
        cell_id += 1

    cell_id = 51
    for t in r_topics:
        t["cell"] = cell_id
        cell_id += 1

    cell_id = 55
    for t in b_topics:
        t["cell"] = cell_id
        cell_id += 1

    topics = sorted(topics, key=lambda x: x["cell"])
    print(topics)


with open(input_file_path, 'r') as f:
    topics = json.load(f)

    assign_short_characters(topics)

    with open("/home/barath/Documents/Neet/matrix.json", "w") as f:
        f.write(str(topics))
        # json.dump(topics, f, indent=4)
