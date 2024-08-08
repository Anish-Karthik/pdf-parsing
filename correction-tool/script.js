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
    data.passage = data.passage.replaceAll("\n\t", " \n\t");
    data.passage = data.passage.replaceAll("\n", " \n");

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
            wordByLine.question += 
                `<span id="${referId}" onclick="clickRef(this)">
                    <span  class="question-no-style ${isTabbed ? "tab" : ""}" >Q${questionNo} </span>
                </span>`;
        }
        wordByLine.html = 
            wordByLine.question + `
                <span class="passage-word ${isTabbed ? "tab" : ""} ${wordByLine.css}" id='${wordByLine.wordId}'> 
                    ${wordByLine.word}
                </span>`;
        if (isLineBreak) {
            wordByLine.html = "<br/>" + wordByLine.html; 
        }
}

function populateDataFromHtml(){
    let wordElements = document.getElementsByClassName("passage-word");
    let currentWordCount = 0;
    let highlights = {};
    let passage = "";
    for (let i = 0; i < wordElements.length; i++) {
        let wordElement =  wordElements[i];
        passage += wordElement.innerHTML;

        let cssClasses = wordElement.getAttribute("class").split(" ");
        let highlightedQuestions = [];
        cssClasses.forEach(cssClass => {
            if (cssClass.startsWith("highlight-")) {
                highlightedQuestions.push(cssClass.replace("highlight-", ""));
                
            }
        });
        highlightedQuestions.forEach(question => {
            if (!highlights[question]) {
                highlights[question] = currentWordCount;
            }
        });

        Object.keys(highlights).forEach(question => {
            if (!highlightedQuestions.includes(question)) {
                console.log(question, highlights[question], currentWordCount - 1);
                delete highlights[question];
            }
        });

        currentWordCount += wordElement.innerHTML.trim().split(" ").length;
    }

    Object.keys(highlights).forEach(question => {
        console.log(question, highlights[question], currentWordCount);
    });
}

function passageHightlight(startIndex, wordsByLine) {
    startIndex.forEach((item) => {
        let start_word = item.start;
        let end_word = item.end;
        for (let i = 0; i < wordsByLine.length; i++) {
            var isHighlighted = i >= start_word && i <= end_word;
            getWord(
                item.referId, 
                wordsByLine[i],
                isHighlighted,i == start_word ? item.qno : undefined,
                isHighlighted ? item.qno : undefined);
        }
    });
    
    return wordsByLine;
}

function clickRef(element) {
    removeHighlightedQuestion();

    let referId = element.id;
    data.questions.forEach((question) => {
        question.references.forEach((ref) => {
            if (ref.referId == referId) {
                document.getElementById("selectedQuestionId").innerText =
                    question.qno + ". " + question.description;
                highlight(data.section, ref.start_word, ref.end_word);
                helper.selectedQuestion = question;
                helper.selectedRef = ref;
                helper.element = element;
                return;
            }
        });
    });
}

function removeHighlightedQuestion() {
    let questionElements = document.getElementsByClassName("questionSection");
    for (let i = 0; i < questionElements.length; i++) {
        questionElements[i].classList.remove("highlightSelection");
    }
}

function modifyRef() {
    console.log("modifyRef ", helper);
    const selectedElements = getSelectedContent();
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
    return append_question_box(wordsByLine, references);
}

function optionHtml(question) {
    return question.options
        .map(
            (option, index) =>
                `<p class = 'option option-${question.qno} ${String.fromCharCode(65 + index) == question.correct_option
                    ? "correct-option"
                    : "incorrect-option"
                }' style="margin-left:20px;">${String.fromCharCode(65 + index)}. ${option.description} <button class="opt-disable-btn">tick</button></p>`
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
    return `<div>${html}</div>` ;
}

function clickQuestionRef(element) {
    removeHighlightedQuestion();

    const questionId = element.id;
    data.questions.forEach((question) => {
        if (question.qno === questionId) {
            document.getElementById("selectedQuestionId").innerHTML =
                question.qno + ". " + question.description;
            helper.selectedQuestion = question;
            element.parentNode.classList.add("highlightSelection");
        }
    });
}

function questionHtml(data) {
    return data.questions
        .map(
            (question) => `
                <div class="questionSection">
                    <div id="${question.qno}" onclick="clickQuestionRef(this)" class="question">
                        <p><strong>Question ${question.qno}:</strong>
                            ${getQuestionDescriptionHtml(
                                data.section, question.description,question.references)}
                        </p>
                    </div>
                    ${optionHtml(question)}
                </div>`
        )
        .join("");
}

function reRender(data) {
    const contentDiv = document.getElementById("content");
    let html = `<div class="section-html">`;
    html += passageHtml(data);
    html += `<div class="question-html">${questionHtml(data)}
        </div>`;
    contentDiv.innerHTML = html;
}

function renderContent(data) {
    // Listen for mouseup event to trigger the function after selection
    document.addEventListener("mouseup", getSelectedContent);
    document.addEventListener("dblclick", getSelectedContent);

    if (!data) return;
    reRender(data);
}

function getSelectedContent() {
    const selection = window.getSelection();
    let selectedText = "";

    // Check if there's an actual selection
    if (selection.rangeCount > 0 && !selection.isCollapsed) {
        const range = selection.getRangeAt(0);
        const selectedElements = [];

        // Get all elements that intersect with the selected range
        document.querySelectorAll("span").forEach((span) => {
            if (range.intersectsNode(span)) {
                selectedText += span.innerHTML;
                selectedElements.push(span);
            }
        });

        document.getElementById("selectedContent").innerHTML = selectedText;

        // Log the attributes of selected elements
        return selectedElements;
    } else {
        document.getElementById("selectedContent").innerHTML = "";
    }
}
function editOptionMode(){
    function handleClick(element,event){
       if(!confirm(`Are you sure you want to change the option to ${element.innerText}`)) return;
        changeCorrectOption(element,event)
    }
   let options = document.getElementsByClassName('option');
   if(document.getElementById('editMode').checked){
     for(let i = 0; i < options.length; i++){
        options[i].getElementsByTagName('button')[0].className = 'opt-change-btn'
        options[i].removeEventListener("click", function(event) {
            handleClick(options[i], event);
        });
        options[i].getElementsByTagName('button')[0].addEventListener("click",function(event) {
            handleClick(options[i], event);
          });
     }
   }else{
    for(let i = 0; i < options.length; i++){
        options[i].getElementsByTagName('button')[0].className = "opt-disable-btn"
     }
   }
}
function changeCorrectOption(element,event){
    let regex = /option-\d{1,}/;
    let classes = Array.from(element.classList)
    let matchingIndex = classes.findIndex(className => regex.test(className));
    all_match_options = document.getElementsByClassName(classes[matchingIndex])
    for(let i = 0;i<all_match_options.length;i++){
       if(Array.from(all_match_options[i].classList).includes(classes[matchingIndex])){
        all_match_options[i].classList.remove("correct-option");
        all_match_options[i].classList.add("incorrect-option");
       }
    }
    element.classList.remove("incorrect-option")
    element.classList.add("correct-option")
}
function editModeChanged() {
    let passageElements = document.getElementsByClassName("passage-word");
    if (document.getElementById('editMode').checked) {
        for (let i = 0; i < passageElements.length; i++) {
            passageElements[i].setAttribute("contenteditable", "true");
        }
    } else {
        for (let i = 0; i < passageElements.length; i++) {
            passageElements[i].setAttribute("contenteditable", "false");
        }
    }
    editOptionMode();
}