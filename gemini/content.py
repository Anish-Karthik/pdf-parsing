underline = ["""25. On December 30, Prime Minist er N arendra
modi launched a hash tag (#IndiaSupportsC AA)
on Twitter
__
th e w hole country
with his government and those who support th e
CAA. If India supports the CAA, are those
protesting tens of thousands out on th e s t reets
not Indian?
A. Criticizing
B. Enormous
C. Conflating
D. Comparing
E. None of the above.

26. To act as a
_________________________
force
against an expansive China, th e U S, Ja pan,
Australia and India formed the Quad.
A. Contrast
B. Countervailing
C. Liquidity
D. Murky
E. None of the above.

27. Marico's biggest achievement i sn't the profits
or turnover or popularity. It's breaking new
ground despite competing __
with
multinationals.
A. Bib and tucker
B. Neck and neck
C. Nip and tuck
D. Both b and c
E. None of the above

28. My commitment to the sport will never
change _
of th e o utcome towards
the award, but getting i t will greatly b enefit th e
sport,
A. Despite
B. Therefore
C. Irrespective
D. Determined
E. None of the above

29. Both the Congress and BJP claim
___________________
that they do not
differentiate between caste Hindus and the
Dalits. The fact is they both do.
A. Vociferously
B. Angrily
C. Arguments
D. Neatly
E. None of the above

30. Once the disrespectful worker was gone, the
office was no longer fi l led with scornful
___
.
A. adherence
B. sanctions
C. derision
D. assistance
E. None of these
"""
,"""Que. 21 Fill in the blank with the appropriate word.
In May 1835 Van Buren was ______ nominated by the Democratic convention at Baltimore.
1. Differently
2. Divergently 3. Oppositely
4. Inconsistently 5. Unanimously
Correct Option - 5

Que. 22 Fill in the blank with the appropriate word.
Rita begged her husband to quit his unhealthy _______ of smoking cigars.
1. Decency 2. Virtue
3. Vice
4. Happiness 5. Honor
Correct Option - 3

Que. 23 Fill in the blanks.
Raymond wrote imaginary tales for young children containing ___________ characters and events like the Wayfarer Merlion who divided the sea.
1. grotesque
2. fantastic
3. corresponding
4. appropriate
5. none of the above
Correct Option - 2

Que. 24 Fill in the blanks.
Mr. Loddstone was ___________ on his henchman to aid in the cover up of the murder.
1. Believing
2. Calculating
3. Accounting
4. Counting
5. None of the above
Correct Option - 4

""",
""" 
Que. 25 Pick out the most appropriate word from the given words to fill in the blank to make the sentence meaningfully correct.
In terms of treating acne, neem paste is observed to ______ much of grease and bacteria that can exacerbate the condition.
1. Keep
2. Create
3. Increase 4. Eliminate 5. Allow
Correct Option - 4

Select the most appropriate word to fill in the blank-
For all their faults, dynastic parties are _____ to build up the personas of their leadership as well as to
resist fragmentation in the long run.
1. thrown 2. designed 3. brighten 4. heighten 5. before
Correct Option - 2

Que. 90 Directions: Select the most appropriate word to fill in the blank.
Therefore, in absence of the required infrastructure, the blame for non-compliance cannot be _______ only to the police officer.
1. Gifted 2. Rifted 3. Shifted 4. Lifted 5. Hefted
Correct Option - 3

Que. 91 Directions: Select the most appropriate word to fill in the blank.
The direct message was that NATO would no longer _______ Russian sensitivities on the subject of NATO expansion.
1. Hinder
2. Alter
3. Deliquesce 
4. Dissipate 
5. Consider
Correct Option - 5

Que. 92 Directions: Select the most appropriate word to fill in the blank.
India’s ruling party’s anti-Muslim inclinations have also _______ additional ammunition to the advocates of “Ghazwa-e-Hind”.
1. Provided
2. Divided
3. Decided
4. Commended 5. Redundant
 
Correct Option - 1
Que. 93 Directions: Select the most appropriate word to fill in the blank.
The Indian education system has been _______ from an elite bias since colonial times.
1. Blistering 2. Despairing 3. Gathering 4. Outpouring 5. Suffering
Correct Option - 5

"""]

underlined_prompt = """
create two fill in the blanks question with multiple choice with atleast two lines
objective type 
with its correct answer and provide reasoning for the correct answer and why other options are wrong.
verify everything is correct


Example:
The direct message was that NATO would no longer _______ Russian sensitivities on the subject of NATO expansion.
1. Hinder
2. Alter
3. Deliquesce 
4. Dissipate 
5. Consider
Correct Option - 5"""

underlined_themes = [
"Indian Elections and Governance",
"Global Conflicts and Crises",
"Climate Change and Environmental Issues",
"International Organizations and Diplomacy",
"Domestic and International Terrorism",
"Economic Indicators and Trends",
"Financial Markets and Investments",
"Corporate Social Responsibility",
"Entrepreneurship and Innovation",
"Global Supply Chains and Trade",
"Olympic Games and Paralympics",
"Major Sporting Events and Championships",
"Sports History and Legends",
"Sports and Technology",
"Sports and Health",
"Human Rights and Civil Liberties",
"Gender Equality and Feminism",
"Education and Social Mobility",
"Poverty and Inequality",
"Urbanization and Rural Development",
"Idioms and Phrases",
"Synonyms and Antonyms",
"Grammar and Usage Rules",
"Vocabulary Building Techniques",
"English Literature and Poetry",
"Science and Technology",
"History and Culture",
"Geography and Environment",
"Arts and Literature",
"Philosophy and Religion",
"Rhetorical Devices and Figurative Language",
"World Mythologies and Folklore",
"Classic and Contemporary Film Analysis",
"Media Literacy and Digital Communication",
"Linguistic Evolution and Language Origins",
"Crossword Puzzles and Word Games",
"Public Speaking and Debate Techniques",
"Multicultural Literature and Diverse Voices",
"Literary Genres and Subgenres",
"Etymology and Word Origins",
"Proverbs and Sayings from Around the World",
"Creative Writing Techniques and Styles",
"Analyzing Advertising and Marketing Language",
"Journalistic Writing and News Literacy",
"Shakespearean Works and Themes",
"Dystopian and Utopian Literature",
"Satire and Social Commentary in Literature",
"Interpreting Poetry and Poetic Devices",
"Nonverbal Communication and Body Language",
"Formal and Informal Language Usage"
]