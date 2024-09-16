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


para_jumbles_prompt="""
Create two para-jumble question with 5 sentences labeled A, B, C, D, and E. 
The sentences should form a coherent paragraph when arranged in the correct order. 
Provide 4 possible sequence options and indicate the correct answer. 
Include a brief reasoning of why the chosen sequence is correct, highlighting key logical connections or transitions between sentences. 
Ensure the topic is interesting and substantive, avoiding overly simplistic or obvious arrangements. 
After presenting the question, verify that the correct sequence indeed forms a logical and well-flowing paragraph.

Example 1:
A. However, recent studies have shown that bees can also perceive and differentiate between various floral scents.
B. Bees have long been known for their remarkable ability to see ultraviolet light, which helps them locate nectar-rich flowers.
C. This combination of visual and olfactory cues allows bees to efficiently identify and remember the most rewarding flower species.
D. These scents act as chemical signals, providing bees with additional information about the flower's nectar quality and quantity.
E. The discovery of this dual sensory system has shed new light on the complex relationship between bees and flowers in pollination.
Options:

BADCE
BACED
CEBAD
ABCDE

Correct Answer: 2. BACED
Explanation: The paragraph should start with B, introducing the known ability of bees to see ultraviolet light. A follows, contrasting this with the recent discovery about scent perception. C explains how bees use both visual and olfactory cues. E concludes by emphasizing the significance of this dual sensory system in understanding bee-flower relationships.
Verify that the sequence BACED forms a logical and coherent paragraph.

Example 2:
Q) In the question given below, some sentences are given, find the sentence which is not really contributing to the main theme and OUT of the passage or find the odd sentence and rearrange the remaining sentences to make a coherent paragraph.

(A) Dozens more were missing.

(B) The deaths occurred in the cities of Guaruja, Santos and Sao Vicente of Sao Paulo state, with the former hardest hit, according to a statement from its civil defence office.

(C) The ban led to plummeting trade volumes and exchanges shutting their businesses.

(D) The office estimates 200 people have been displaced in Guaruja.

(E) A storm that pummeled Brazil’s south-eastern coast early Tuesday caused landslides and killed at least 16 people.

E-B-D-A-C
C-D-A-E
E-A-B-D
D-C-B-E-A

Correct Answer:  3. E-A-B-D
Explanation: After going through all the given five sentences, we can easily mark sentence C as the odd one it is talking about businesses but this whole paragraph is about landslides and casualties."""

para_jumbles_theme=[
    "The history of ancient civilizations",
    "Climate change and its effects",
    "Space exploration milestones",
    "The evolution of social media",
    "Artificial intelligence in everyday life",
    "Traditional cuisines around the world",
    "The impact of plastic pollution on marine life",
    "The rise of e-commerce",
    "Renewable energy sources",
    "The psychology of decision-making",
    "The global coffee industry",
    "The role of exercise in mental health",
    "The history of currency and banking",
    "The evolution of human languages",
    "Sustainable urban planning",
    "The impact of music on cognitive development",
    "The ethics of genetic engineering",
    "The psychology of color in marketing",
    "The history of Olympic Games",
    "The future of work and automation",
    "The impact of tourism on local economies",
    "The science behind climate prediction",
    "The evolution of storytelling in different media",
    "The importance of sleep for overall health",
    "The global water crisis and potential solutions",
    "The psychology of consumer behavior",
    "The history and future of robotics",
    "The impact of social media on politics",
    "The science of happiness and well-being",
    "The evolution of agriculture and food production",
    "The role of art in society",
    "The future of education and learning",
    "The psychology of addiction and recovery",
    "The impact of deforestation on ecosystems",
    "The history and cultural significance of tea",
    "The science behind renewable energy storage",
    "The evolution of fashion and its cultural impact",
    "The psychology of leadership and teamwork",
    "The global impact of microplastics",
    "The future of space colonization",
    "The role of fungi in ecosystems and human use",
    "The impact of video games on cognitive skills",
    "The history and future of cryptocurrency",
    "The psychology of habit formation",
    "The evolution of human nutrition",
    "The impact of light pollution on wildlife",
    "The science of memory and learning",
    "The future of healthcare and personalized medicine",
    "The history and development of the internet",
    "The psychology of creativity and innovation",
]