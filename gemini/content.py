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

para_jumbles_themes=[
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

cloze_test_prompt = """
Create two cloze test passage of 4-5 sentences.
Include 5 blanks in the passage, labeled (A) through (E). For each blank, ask a question and provide 5 multiple-choice options.
give the correct answers for each of the 5 questions and give detailed explanations, reasoning for why each correct option fits best and why the other options are incorrect.
Consider grammar, context, and meaning when explaining the choices. Ensure that the passage flows logically and that all options are plausible within the context.
Verify the accuracy and coherence of the entire question, including the passage,questions, options, and explanations.

Example:
P1. Directions: Provide the appropriate tense form of the verbs in brackets. Joe was very unhappy with her standard of living. Her dad went bankrupt a few years ago and hence her family was poor. All her clothes were shabby and old and they _______ (look) like they would _______ (tear) any moment. She _______ (envy) the girls who wore pretty frocks to school. They would also bring tasty snacks to _______ (eat) during the break while she always had to make do with plain bread and butter. One day she _______ (bawl) her eyes out in her room because she couldn’t take it anymore when suddenly her mother entered.

Q1. Which is the correct form of the verb that should come in blank 1?

looked
had looked
looks
will look
will be looking
Ans. We have to use the simple past tense of the verb ‘look’ which is ‘looked’. The story is written in the past tense. Notice that verbs like ‘was’ and ‘were’ are used before. For a story written in the past tense, most of the verbs will be in the simple past tense (verbs can also take other versions of the past tense). The simple past tense shows that you are talking about something that has already happened. Unlike the past continuous tense, which is used to talk about past events that happened over a period of time, the simple past tense emphasizes that the action is finished. The other options are wrong as they make the sentence grammatically incorrect.

Q2. Which is the correct form of the verb that should come in blank 2?

tore
had torn
tear
tears
will tore
Ans. We have to use the base form of the verb ‘tear’ which is ‘tear’ itself. Notice that the modal/auxiliary verb ‘would’ is used before the blank. ‘Would’ is followed by the main verb. The main verb stays in its base form. The main verb that is used with ‘would’ does not change form according to the subject.

To get details on Common Rules for Spellings, candidates can visit the linked article.

Q3. Which is the correct form of the verb that should come in blank 3?

envies
envied
had been envied
Envy
will envy
Ans. We have to use the simple past tense of the verb ‘envy’ which is ‘envied’. The story is written in the past tense. Notice that verbs like ‘was’ and ‘were’ are used before. For a story written in the past tense, most of the verbs will be in simple past (verbs can also take other versions of the past tense). The simple past tense shows that you are talking about something that has already happened. Unlike the past continuous tense, which is used to talk about past events that happened over a period of time, the simple past tense emphasizes that the action is finished. The other options are wrong as they make the sentence grammatically incorrect.

Q4. Which is the correct form of the verb that should come in blank 4?

had eaten
was eating
eats
eat
will eat
Ans. We have to use the base form of the verb ‘eat’ which is ‘eat’ itself. Notice that there is ‘to’ before the blank. The base form of a verb appears in the infinitive form. The infinitive form of a verb is the verb in its basic form. It is the version of the verb which will appear in the dictionary. The infinitive form of a verb is usually preceded by to (e.g., to run, to dance, to think). The other options are wrong as they make the sentence grammatically incorrect.

For details on the Synonyms & Antonyms, refer to the linked article.

Q5. Which is the correct form of the verb that should come in blank 5?

was bawling
bawls
had bawled
is bawling
will be bawling
Ans. We have to use the past continuous tense of the verb ‘bawl’ which is ‘was bawling’. The past continuous tense refers to a continuing action or state that was happening at some point in the Past. It is formed by combining the past tense of to be (i.e., was/were) with the verb’s present participle (-ing word). It can also be used to describe something that was happening continuously in the past when another action interrupted it. Eg: I was talking to Jessica when he suddenly showed up."""


cloze_test_themes = [
    "Caste System and Social Structures in India – Understanding the origins of social classifications in ancient India.",
    "Language Usage: Adjective Selection – Identifying appropriate adjectives to fill in missing blanks in a sentence.",
    "Vocabulary: Noun Usage – Selecting correct nouns to complete the meaning of sentences.",
    "Verbs in Historical Context – Choosing the correct verbs for past historical events or processes.",
    "Verb Usage: Infinitive Form – Filling blanks with the appropriate infinitive verb forms.",
    "Tense: Simple Past in Narratives – Completing stories with the correct simple past tense verbs.",
    "Verbs with Modal Auxiliaries – Identifying the base form of verbs when used with modal auxiliaries like 'would' or 'could'.",
    "Past Tense Usage: Simple vs. Progressive – Choosing between simple past and past continuous tense in descriptive sentences.",
    "Infinitive Forms in Narrative Contexts – Filling sentences with the correct infinitive verb forms where necessary.",
    "Past Continuous Tense – Selecting past continuous forms to describe ongoing actions in the past.",
    "Adjective Agreement in Complex Sentences – Filling blanks with adjectives that correctly agree with nouns.",
    "Adverbs of Frequency and Intensity – Completing sentences with appropriate adverbs of frequency or intensity.",
    "Conditional Sentences (First and Second) – Filling blanks with correct verbs to form conditionals.",
    "Past Perfect vs. Past Continuous – Choosing the correct past perfect or past continuous tense forms in narrative contexts.",
    "Direct and Indirect Speech – Filling in blanks with the correct verb forms in direct and reported speech.",
    "Subject-Verb Agreement in Complex Sentences – Ensuring correct subject-verb agreement in multi-clause sentences.",
    "Cultural References in Language Usage – Identifying words or phrases influenced by culture to complete sentences.",
    "Prepositions in Spatial Contexts – Filling blanks with correct prepositions indicating location or direction.",
    "Phrasal Verbs in Daily Communication – Completing sentences with common phrasal verbs.",
    "Synonyms and Antonyms – Filling in blanks with appropriate synonyms or antonyms.",
    "Transition Words for Flow and Coherence – Choosing transition words to improve flow between sentences.",
    "Pronoun-Antecedent Agreement – Filling in blanks with pronouns that match their antecedents in sentences.",
    "Idiomatic Expressions and Their Origins – Completing sentences with idiomatic expressions.",
    "Contextual Vocabulary Usage in Business English – Filling blanks with appropriate business-related vocabulary.",
    "Homophones and Commonly Confused Words – Filling blanks with correct homophones or commonly confused words.",
    "Abstract Nouns and Their Uses – Choosing appropriate abstract nouns to complete the meaning of sentences.",
    "Active vs. Passive Voice in Academic Writing – Identifying the correct voice (active or passive) to complete academic sentences.",
    "Expressing Comparisons: Comparative and Superlative Forms – Filling in blanks with comparative or superlative forms.",
    "Forming and Using Compound Sentences – Completing sentences with the correct conjunctions to form compound sentences.",
    "Figurative Language in Poetry – Completing poetic lines with figurative language like metaphors or similes.",
    "Technical Vocabulary in Science and Technology – Filling blanks with specialized scientific or technical vocabulary.",
    "Gender-Neutral Language in Modern English – Filling in blanks with gender-neutral terms.",
    "Formality Levels in Different Writing Contexts – Choosing vocabulary to match the level of formality required in context.",
    "Prefixes and Suffixes in Word Formation – Filling blanks with words formed using correct prefixes or suffixes.",
    "Using Quantifiers Correctly – Filling blanks with appropriate quantifiers like 'some', 'many', or 'few'.",
    "Collocations in Professional Communication – Completing sentences with common word pairings or collocations.",
    "Pronunciation Patterns and Stress in English Words – Filling in blanks with words that match pronunciation patterns.",
    "Tense Shifts in Narrative Writing – Maintaining tense consistency by filling blanks with the correct verb tense.",
    "Redundancy and Conciseness in Writing – Filling in blanks with concise wording, avoiding redundancy.",
    "Paraphrasing and Summarizing Techniques – Completing sentences with paraphrased or summarized content.",
    "Negation in English Sentences – Filling blanks with negative forms to correctly negate a sentence.",
    "Analogies in Argumentative Writing – Completing arguments with appropriate analogies.",
    "Descriptive Language in Travel Writing – Filling blanks with descriptive language to enhance travel writing.",
    "Conjunctions in Linking Ideas – Filling in blanks with conjunctions to connect ideas logically.",
    "Using Conditionals for Predictions – Filling blanks with conditionals to express future predictions.",
    "Rhetorical Devices in Persuasive Writing – Completing sentences with rhetorical devices like ethos or pathos.",
    "Sentence Fragments vs. Complete Sentences – Identifying and correcting sentence fragments to complete sentences.",
    "Articles (Definite, Indefinite, Zero) in English – Filling blanks with appropriate articles.",
    "Cultural Sensitivity in Language – Filling blanks with culturally sensitive and unbiased language.",
    "Hyperbole and Understatement – Filling sentences with hyperbole or understatement for dramatic effect."
]

sample_questions = """
Que. 37 If the marked price of a laptop is Rs. 24,000 which is 20% more than the cost price. The laptop is sold
at a profit of Rs. 1000. Find the discount%.
1. 12.5% 2. 21.5% 3. 22.5% 4. 25% 5. 50%
Correct Option - 1

Que. 38 T alone can complete the work in 12 days. T and U together worked on a piece of work and completed
one-third work in 3 days. In how many days can U alone complete the same piece of work?
1. 36 days
2. 40 days
3. 25 days
4. 30 days
5. 34 days
Correct Option - 1

Que. 40 The marked price of an article is 50% above its cost price. If the marked price is Rs. 600, and the profit
is 30%. Find the selling price of the article?
1. Rs. 525
2. Rs. 515
3. Rs. 510
4. Rs. 530
5. None of these
Correct Option - 5

42 If the respective ratio of the number of bikes sold by company 'Y' in 2021 to that by company 'D' in the same year is 7:8 then what is the average number of bikes sold by companies 'Y', 'A', 'B', and 'C'
together in 2021?
1. 720 2. 760 3. 780 4. 800 5. 820
Correct Option - 1
"""

neet_biology_questions="""
Q.1. In plants, the end product of anaerobic respiration is
(1) lactic acid
(2) pyruvic acid
(3) methyl alcohol
(4) ethyl alcohol.

Answer
(4) 
 

Q.2. Assertion (A): A typical microsporangium of angiosperm is generally surrounded by four wall layers.
Reason (R): The outer three wall layers perform the function of protection and help in dehiscence of anther to release the pollen.
(1) Both (A) and (R) are correct and (R) is the correct explanation of (A).
(2) Both (A) and (R) are correct but (R) is not the correct explanation of (A).
(3) (A) is correct but (R) is not correct.
(4) (A) is not correct but (R) is correct.

Answer
(2) 
 

Q.3. Which of the following are the characteristics of expanding population?
(i) Pyramid – shaped age structure
(ii) An urn – shaped age structure
(iii) Pre-reproductive and reproductive age groups become more or less equal in size
(iv) Rapidly growing population with high birth rates.
(1) (i) and (ii) (2) (i) and (iv)
(3) (iii) and (iv) (4) (ii) and (iii)

Answer
(2) 
 

Q.4. Perisperm differs from endosperm in
(1) being a diploid tissue
(2) its formation by fusion of secondary nucleus with several sperms
(3) being a haploid tissue
(4) having no reserve food.

Answer
(1) 
 

Q.5. Which cell organelle is related to glycoprotein formation?
(1) Golgi apparatus
(2) Rough endoplasmic reticulum
(3) Glyoxysome
(4) Mitochondria

Answer
(1) 
 

Q.6. Mendelian recombinations are due to
(1) linkage
(2) independent assortment of genes
(3) mutations
(4) dominant characters.

Answer
(4) 
 

Q.7. Bicarpellary gynoecium and oblique ovary is found in
(1) Solanum melongena
(2) Sesbania
(3) Pisum sativum
(4) Brassica campestris.

Answer
(3) 
 

Q.8. Select the incorrect pair.
(1) Mitochondria-Oxidative phosphorylation
(2) Endoplasmic reticulum-Protein synthesis
(3) Chloroplast-Photosynthesis
(4) Golgi apparatus-Breakdown of complex macromolecules

Answer
(4) 
 

Q.9. Identify the cross that will result in the formation of tall and dwarf pea plants in same (equal) proportions?
(1) TT × tt (2) tt × tt (3) TT × Tt (4) Tt × tt

Answer
(1) 
 

Q.10. The floral formula, belongs to Family



(1) Fabaceae (2) Solanaceae
(3) Compositae (4) Leguminosae.

Answer
(4) 
"""