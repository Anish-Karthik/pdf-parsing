var helper = {};
var data = [];
function downloadJSONFile(data, filename = "data.json") {
    const jsonStr = JSON.stringify(data, null, 2);
    const blob = new Blob([jsonStr], { type: "application/json" });
    const link = document.createElement("a");
    link.href = window.URL.createObjectURL(blob);
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

function uploadFile() {
    const fileInput = document.getElementById("fileInput");
    const file = fileInput.files[0];

    if (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
            try {
                const jsonData = JSON.parse(e.target.result);
                data = jsonData;
                preprocessData();
                console.log("preprocess data",data)
                renderContent(data);
            } catch (error) {
                console.log(error); //
            }
        };
        reader.readAsText(file);
    } else {
        alert("No file selected");
    }
}

function preprocessData() {
    data.passage = data.passage.replace("\n\t", " \n\t");
    data.passage = data.passage.replace("\n", " \n");

    passageWords = data.passage.split(" ");
    data.words = [];
    for (i = 0; i < passageWords.length; i++) {
        data.words.push({"wordId": `1-1-${i}`, "word": passageWords[i]});
    }

}

function delRef() {
    console.log(helper);
    if (!helper.selectedRef) {
        alert("No reference is selected");
    }
    data.questions.forEach((question, index) => {
        if (question.qno == helper.selectedQuestion.qno) {
            console.log(data.questions[index].references);
            data.questions[index].references = question.references.filter(
                (ref, index) => {
                    return ref.id != helper.selectedRef.id;
                }
            );
            console.log(data.questions[index].references);
        }
    });
    helper.element = null;
    helper.selectedRef = null;
    renderContent(data);
}

function getWord(referId,wordByLine, isHighlighted,questionNo,highlightQno){
        let isTabbed = false;
        let isLineBreak = false;
        if (wordByLine.word.startsWith("\n\t")) {
            isTabbed = true;
            isLineBreak = true;
        }
        if (wordByLine.word.startsWith("\n")) {
            isLineBreak = true;
        }
        if(isHighlighted){
            wordByLine.css += ` highlighted  highlight-${highlightQno}`;
        }
        
        if (questionNo) {
            wordByLine.question += `<span id="${referId}" onclick="clickRef(this)">
                    <span  class="question-no-style ${isTabbed ? "tab" : ""}" >Q${questionNo} </span>
                </span>`;
        }
        wordByLine.html = wordByLine.question + `<span class="${wordByLine.css}" id='${wordByLine.wordId}'> ${wordByLine.word}</span>`;
        if (isLineBreak) {
            wordByLine.html = "<br/>" + wordByLine.html; 
        }
}
function updateReference(){
    let refId; 
    data.questions.forEach((question)=>{
       var elements = document.getElementsByClassName(`highlight-${question.qno}`)
       for(let i = 0; i < elements.length; i++){
        console.log(elements[i].innerHTML)
       }
    })
}
function passageHightlight(startIndex, wordsByLine) {
    console.log("inside passageHightlight",wordsByLine)
    startIndex.forEach((item) => {
        let start_word = item.start;
        let end_word = item.end;
        for (let i = 0; i < wordsByLine.length; i++) {
            var isHighlighted = i >= start_word && i <= end_word;
            getWord(item.referId, wordsByLine[i],isHighlighted,i == start_word ? item.qno : undefined,isHighlighted ? item.qno : undefined)
        }
        // for (let i = 0; i < wordsByLine.length; i++) {
        //     let isTabbed = false;
        //     let isLineBreak = false;
        //     if (wordsByLine[i].word.startsWith("\n\t")) {
        //         isTabbed = true;
        //         isLineBreak = true;
        //     }
        //     if (wordsByLine[i].word.startsWith("\n")) {
        //         isLineBreak = true;
        //     }
    
        //     if (i >= start_word && i <= end_word) {
                
        //         if (i == start_word) {
        //             wordsByLine[i].html =
        //                 `<span id="${item.referId}" onclick="clickRef(this)">
        //                     <span  class="question-no-style ${isTabbed ? "tab" : ""} highlight-${item.qno}" >Q${item.qno} </span>
        //                 </span>
        //                 <span class="highlighted" id='${wordsByLine[i].wordId}'> ${wordsByLine[i].word}</span>`;
        //         } else if (wordsByLine[i].html == "") {
        //             wordsByLine[i].html =
        //                 `<span class="highlighted ${isTabbed ? "tab" : ""}" id='${wordsByLine[i].wordId}'> ${wordsByLine[i].word}</span>`;
        //         }
                
        //         if (isLineBreak) {
        //             wordsByLine[i].html = "<br/>" + wordsByLine[i].html; 
        //         }
        //     }
        // }
    });
    // for (let i = 0; i < wordsByLine.length; i++) {
    //     let isTabbed = false;
    //     let isLineBreak = false;
    //     if (wordsByLine[i].word.startsWith("\n\t")) {
    //         isTabbed = true;
    //         isLineBreak = true;
    //     }
    //     if (wordsByLine[i].word.startsWith("\n")) {
    //         isLineBreak = true;
    //     }
    //     if (wordsByLine[i].html == "") {
    //         wordsByLine[i].html = `<span class="${isTabbed ? "tab" : ""}" id='${wordsByLine[i].wordId}'> ${wordsByLine[i].word}</span>`;
    //         if (isLineBreak) {
    //             wordsByLine[i].html = "<br/>" + wordsByLine[i].html; 
    //         }
    //     }
    // }
    return wordsByLine;
}

function clickRef(element) {
    let referId = element.id;
    data.questions.forEach((question) => {
        question.references.forEach((ref) => {
            if (ref.referId == referId) {
                document.getElementById("selectedQuestionId").innerText =
                    question.qno + ". " + question.description;
                document.getElementById("modifyStartRef").innerText =
                    ref.start_word;
                document.getElementById("modifyEndRef").innerText = ref.end_word;
                highlight(data.section, ref.start_word, ref.end_word);
                helper.selectedQuestion = question;
                helper.selectedRef = ref;
                helper.element = element;
                return;
            }
        });
    });
}

function modifyRef() {
    console.log("modifyRef ", helper);
    const selectedElements = logSelectedAttributes();
    if (!selectedElements) {
        alert("No text is selected");
        return;
    }
    if (!helper.selectedRef && helper.element) {
        alert("No reference selected.");
        return;
    }
    let startWord = selectedElements[0].id.split("-")[2];
    let endWord =
        selectedElements[selectedElements.length - 1].id.split("-")[2];

    if (helper.element) {
        data.questions.forEach((question) => {
            if (question.qno == helper.selectedQuestion.qno) {
                question.references.forEach((ref, index) => {
                    if (ref.referId === helper.selectedRef.referId) {
                        question.references[index].start_word = startWord;
                        question.references[index].end_word = endWord;
                    }
                });
            }
        });
        helper.element = null;
    } else {
        console.log("hello");
        document.getElementById("modifyStartRef").innerHTML = startWord;
        document.getElementById("modifyEndRef").innerHTML = endWord;

        data.questions.forEach((question, ind) => {
            if (question.qno === helper.selectedQuestion.qno) {
                data.questions[ind].references.push({
                    referId:
                        data.section +
                        "-" +
                        1 +
                        "-" +
                        data.questions[ind].references.length,
                    start_word: startWord,
                    end_word: endWord,
                });
            }
        });
        console.log(data);
        renderContent(data);
    }
    renderContent(data);
}

function append_question_box(wordsByLine, references) {
    var startIndex = [];
    references.forEach((item) => {
        let q_no = item.qno;
        item.references.forEach((ref) => {
            startIndex.push({
                qno: q_no,
                referId: ref.referId,
                start: ref.start_word,
                end: ref.end_word,
            });
        });
    });
    startIndex.sort((a, b) => a.start - b.start);
    var html = ``;
    wordsByLine = passageHightlight(startIndex, wordsByLine);
    wordsByLine.forEach((word, wordInde) => {
        html += word.html;
    });
    return `${html}</div>`;
}

function passageHtml(data) {
    const references = data.questions
        .map((question) => {
            if (question.references == 0) return;
            return { qno: question.qno, references: question.references };
        })
        .filter((reference) => reference);

    wordsByLine = data.words.map((word) => {
        return {question : ``, css : ``, html: ``, ...word };
    });
    console.log("wordsByLine", wordsByLine)
    return append_question_box(wordsByLine, references);
}

function optionHtml(question) {
    return question.options
        .map(
            (option, index) =>
                `<p class = '${String.fromCharCode(65 + index) == question.correct_option
                    ? "correct-option"
                    : "incorrect-option"
                }'>${String.fromCharCode(65 + index)}. ${option.description}</p>`
        )
        .join("");
}

function highlight(section, start, end, timeout = 4000) {
    for (let i = start; i <= end; i++) {
        document.getElementById(`${section}-1-${i}`).style.background =
            "yellow";
    }
    if (timeout > 0) {
        setTimeout(() => {
            for (let i = start; i <= end; i++) {
                document.getElementById(`${section}-1-${i}`).style.background =
                    "";
            }
        }, timeout);
    }
}

function getQuestionDescriptionHtml(
    section_no,
    questionDescription,
    references
) {
    const patterns = [
        /Lines\s+(\d+)\s*-\s*(\d+)/i,
        /Line\s+(\d+)/i,
        /Lines\s+(\d+)\s*and\s*(\d+)/i,
    ];
    let matches = [];

    patterns.forEach((pattern) => {
        let match = pattern.exec(questionDescription);
        if (match) {
            matches.push({
                start: match.index,
                end: match.index + match[0].length,
            });
        }
    });

    if (matches.length === 0) return questionDescription;

    let html = "";
    let ptr = 0;

    for (let i = 0; i < questionDescription.length; i++) {
        if (
            ptr < matches.length &&
            ptr < references.length &&
            i === matches[ptr].start
        ) {
            let startId = `${section_no}1${references[ptr].start_word}`;
            html += `<a onclick="highlight(${section_no},${references[ptr].start_word
                },${references[ptr].end_word
                })" href='#${startId}'>${questionDescription.slice(
                    i,
                    matches[ptr].end + 1
                )}</a>`;
            i = matches[ptr].end;
            ptr++;
        } else {
            html += questionDescription[i];
        }
    }
    return html;
}

function clickQuestionRef(element) {
    const questionId = element.id;
    element.style.backgroundColor = "yellow";
    data.questions.forEach((question) => {
        if (question.qno === questionId) {
            document.getElementById("selectedQuestionId").innerHTML =
                question.qno + ". " + question.description;
            helper.selectedQuestion = question;
        }
    });
    setTimeout(() => {
        element.style.backgroundColor = "";
    }, 1000);
}

function questionHtml(data) {
    return data.questions
        .map(
            (question) =>
                `<div>
                <div class="question">
                    <p><strong id="${question.qno}" onclick="clickQuestionRef(this)" >Question ${question.qno}:</strong>
                    ${getQuestionDescriptionHtml(
                    data.section,
                    question.description,
                    question.references
                )}
                    </p>
                </div>
                    ${optionHtml(question)}
            </div>`
        )
        .join("");
}

function reRender(data) {
    const contentDiv = document.getElementById("content");
    let html = `<div class="section-html">
            <h1 class="section">Section: ${data.section}</h1>`;
    html += passageHtml(data);
    html += `<div class="question-html">${questionHtml(data)}
        </div>`;
    contentDiv.innerHTML = html;
}

function renderContent(data) {
    // Listen for mouseup event to trigger the function after selection
    document.addEventListener("mouseup", logSelectedAttributes);
    document.addEventListener("dblclick", logSelectedAttributes);

    if (!data) return;
    reRender(data);
}

function logSelectedAttributes() {
    const selection = window.getSelection();

    // Check if there's an actual selection
    if (selection.rangeCount > 0 && !selection.isCollapsed) {
        const range = selection.getRangeAt(0);
        const selectedElements = [];

        // Get all elements that intersect with the selected range
        document.querySelectorAll("span").forEach((span) => {
            if (range.intersectsNode(span)) {
                selectedElements.push(span);
            }
        });

        // Log the attributes of selected elements
        return selectedElements;
    }
}