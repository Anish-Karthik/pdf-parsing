import re
def isquestionare(hpos,element) -> bool:
    for i in hpos:
        if ((element[0] >= i+17 and element[0] <= i + 18) or element[0] == i):
            return True
    return False

def isnextqn(element, prev):
    return abs(prev[1]-element[1]) > 50 or abs(prev[0]-element[0]) > 50

def isanoption(element) -> bool:
    return re.search(r"(?<!.)[A-D]\) ", element[4])