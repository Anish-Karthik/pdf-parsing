import json

with open("College Duniya SAT Sample Passage 2.json", "r") as f:
    json = json.load(f)

writing_rules = """

The Writing Comprehension must have,

Questions often ask about how to improve the text, identify errors, or suggest alternative phrasing.
To create writing comprehension questions, you would typically:

Provide a sample text with errors or areas for improvement.
Ask questions that require the test-taker to identify and correct errors, suggest alternative phrasing, or improve the overall effectiveness of the text.
Focus on aspects like grammar, syntax, word choice, organization, and clarity.
Example Writing Comprehension Question:

The following sentence contains an error. Choose the best revision:
Original sentence: "Me and my friends went to the movies."
A) My friends and me went to the movies.
B) Me and my friends went to the movies.
C) My friends and I went to the movies.
D) I and my friends went to the movies.
Key Differences:

Writing comprehension focuses on how well something is written.
By understanding these distinctions, you can create questions that accurately assess a test-taker's writing skills.

Revision: Improve clarity, conciseness, and effectiveness of written expression. Identify and correct errors in grammar, syntax, and word choice. Refine sentence structure for better clarity.
Development and Organization: Strengthen the focus and coherence of a passage. Add, delete, or rearrange text to improve the passage's structure and logic.
Style and Register: Adapt language and tone to suit the specific context and audience. Demonstrate awareness of appropriate style and register.
Standard English Conventions

Sentence Structure: Identify and correct errors in grammar, syntax, and sentence construction. Understand the rules of grammar and apply them correctly.
Usage: Choose precise words and phrases to convey meaning accurately. Select appropriate vocabulary to express ideas clearly and precisely.
Punctuation: Use punctuation correctly to enhance clarity and meaning. Understand the rules of punctuation and how to use them to structure sentences effectively."""

similar_questions = """{
  "section": 1,
  "passage": "Long viewed by many as the stereotypical useless\nmajor, philosophy is now being seen by many students\nand prospective employers as in fact a very useful and\npractical major, offering students a host of transferable\nskills with relevance to the modern workplace. 34 In\nbroad terms, philosophy is the study of meaning and the\nvalues underlying thought and behavior. But 35 more\npragmatically, the discipline encourages students to\nanalyze complex material, question conventional beliefs,\nand express thoughts in a concise manner.\n\tBecause philosophy 36 teaching students not what\nto think but how to think, the age-old discipline offers\nconsistently useful tools for academic and professional\nachievement. 37 A 1994 survey concluded that only\n18 percent of American colleges required at least one\nphilosophy course. 38 Therefore, between 1992 and\n1996, more than 400 independent philosophy\ndepartments were eliminated from institutions.\n\tMore recently, colleges have recognized the\npracticality and increasing popularity of studying\nphilosophy and have markedly increased the number of\nphilosophy programs offered. By 2008 there were\n817 programs, up from 765 a decade before. In addition,\nthe number of four-year graduates in philosophy has\ngrown 46 percent in a decade. Also, studies have found\nthat those students who major in philosophy often do\nbetter than students from other majors in both verbal\nreasoning and analytical 39 writing. These results can be\nmeasured by standardized test scores. On the Graduate\nRecord Examination (GRE), for example, students\nintending to study philosophy in graduate school 40 has\nscored higher than students in all but four other majors.\n\tThese days, many 41 student\u2019s majoring in\nphilosophy have no intention of becoming philosophers;\ninstead they plan to apply those skills to other disciplines.\nLaw and business specifically benefit from the\ncomplicated theoretical issues raised in the study of\nphilosophy, but philosophy can be just as useful in\nengineering or any field requiring complex analytic skills.\n42 That these skills are transferable across professions\n43 which makes them especially beneficial to\ntwenty-first-century students. Because today\u2019s students\ncan expect to hold multiple jobs\u2014some of which may not\neven exist yet\u2014during 44 our lifetime, studying\nphilosophy allows them to be flexible and adaptable.\nHigh demand, advanced exam scores, and varied\nprofessional skills all argue for maintaining and\nenhancing philosophy courses and majors within\nacademic institutions.",
  "questions": [
    {
      "qno": "34",
      "description": "",
      "options": [
        {
          "description": "NO CHANGE ",
          "reference": null
        },
        {
          "description": "For example, ",
          "reference": null
        },
        {
          "description": "In contrast, ",
          "reference": null
        },
        {
          "description": "Nevertheless, ",
          "reference": null
        }
      ],
      "correct_option": "A",
      "detailed_answer": null,
      "references": []
    },
    {
      "qno": "35",
      "description": "",
      "options": [
        {
          "description": "NO CHANGE ",
          "reference": null
        },
        {
          "description": "speaking in a more pragmatic way, ",
          "reference": null
        },
        {
          "description": "speaking in a way more pragmatically, ",
          "reference": null
        },
        {
          "description": "in a more pragmatic-speaking way, ",
          "reference": null
        }
      ],
      "correct_option": "A",
      "detailed_answer": null,
      "references": []
    },
    {
      "qno": "36",
      "description": "",
      "options": [
        {
          "description": "NO CHANGE ",
          "reference": null
        },
        {
          "description": "teaches ",
          "reference": null
        },
        {
          "description": "to teach ",
          "reference": null
        },
        {
          "description": "and teaching ",
          "reference": null
        }
      ],
      "correct_option": "B",
      "detailed_answer": null,
      "references": []
    },
    {
      "qno": "37",
      "description": "Which choice most effectively sets up the information that follows? ",
      "options": [
        {
          "description": "Consequently, philosophy students have been receiving an increasing number of job offers. ",
          "reference": null
        },
        {
          "description": "Therefore, because of the evidence, colleges increased their offerings in philosophy. ",
          "reference": null
        },
        {
          "description": "Notwithstanding the attractiveness of this course of study, students have resisted majoring in philosophy. ",
          "reference": null
        },
        {
          "description": "However, despite its many utilitarian benefits, colleges have not always supported the study of philosophy. ",
          "reference": null
        }
      ],
      "correct_option": "D",
      "detailed_answer": null,
      "references": []
    },
    {
      "qno": "38",
      "description": "",
      "options": [
        {
          "description": "NO CHANGE ",
          "reference": null
        },
        {
          "description": "Thus, ",
          "reference": null
        },
        {
          "description": "Moreover, ",
          "reference": null
        },
        {
          "description": "However, ",
          "reference": null
        }
      ],
      "correct_option": "C",
      "detailed_answer": null,
      "references": []
    },
    {
      "qno": "39",
      "description": "Which choice most effectively combines the sentences at the underlined portion? ",
      "options": [
        {
          "description": "writing as ",
          "reference": null
        },
        {
          "description": "writing, and these results can be ",
          "reference": null
        },
        {
          "description": "writing, which can also be ",
          "reference": null
        },
        {
          "description": "writing when the results are ",
          "reference": null
        }
      ],
      "correct_option": "A",
      "detailed_answer": null,
      "references": []
    },
    {
      "qno": "40",
      "description": "",
      "options": [
        {
          "description": "NO CHANGE ",
          "reference": null
        },
        {
          "description": "have scored ",
          "reference": null
        },
        {
          "description": "scores ",
          "reference": null
        },
        {
          "description": "scoring ",
          "reference": null
        }
      ],
      "correct_option": "B",
      "detailed_answer": null,
      "references": []
    },
    {
      "qno": "41",
      "description": "",
      "options": [
        {
          "description": "NO CHANGE ",
          "reference": null
        },
        {
          "description": "students majoring ",
          "reference": null
        },
        {
          "description": "students major ",
          "reference": null
        },
        {
          "description": "student\u2019s majors ",
          "reference": null
        }
      ],
      "correct_option": "B",
      "detailed_answer": null,
      "references": []
    },
    {
      "qno": "42",
      "description": "At this point, the writer is considering adding the following sentence. The ancient Greek philosopher Plato, for example, wrote many of his works in the form of dialogues. Should the writer make this addition here? ",
      "options": [
        {
          "description": "Yes, because it reinforces the passage\u2019s main point about the employability of philosophy majors. ",
          "reference": null
        },
        {
          "description": "Yes, because it acknowledges a common counterargument to the passage\u2019s central claim. ",
          "reference": null
        },
        {
          "description": "No, because it blurs the paragraph\u2019s focus by introducing a new idea that goes unexplained. ",
          "reference": null
        },
        {
          "description": "No, because it undermines the passage\u2019s claim about the employability of philosophy majors. ",
          "reference": null
        }
      ],
      "correct_option": "C",
      "detailed_answer": null,
      "references": []
    },
    {
      "qno": "43",
      "description": "",
      "options": [
        {
          "description": "NO CHANGE ",
          "reference": null
        },
        {
          "description": "that ",
          "reference": null
        },
        {
          "description": "and ",
          "reference": null
        },
        {
          "description": "DELETE the underlined portion. ",
          "reference": null
        }
      ],
      "correct_option": "D",
      "detailed_answer": null,
      "references": []
    },
    {
      "qno": "44",
      "description": "",
      "options": [
        {
          "description": "NO CHANGE ",
          "reference": null
        },
        {
          "description": "one\u2019s ",
          "reference": null
        },
        {
          "description": "his or her ",
          "reference": null
        },
        {
          "description": "their ",
          "reference": null
        }
      ],
      "correct_option": "D",
      "detailed_answer": null,
      "references": []
    }
  ]
}"""

prompt = f"""output: python list
Generate 10 SAT writing comprehension questions to test the user's English authoring skills for this passage that are clearly not reading comprehension,
which tests the writer's ability to analyze and engage with complex texts. and avoid graph based quesions
create questions with the following rules:{writing_rules}

read this similar questions and create questions with the following rules:{similar_questions}

From this Passage form questions: {json["passage"]}

    format: [question,[op1,op2,op3,op4],correct_option("A" or "B" or "C" or "D")]  

    return: list[question] output as python list"""
