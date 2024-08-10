var helper = {};
var data = [];
var referenceCount = 0;
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
                helper = structuredClone(data);
                preprocessData();
                console.log("preprocess data",data)
                renderContent(helper);
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
    helper.passage = helper.passage.replaceAll("\n\t", " \n\t");
    // helper.passage = helper.passage.replaceAll("\n", " \n");

    passageWords = helper.passage.split(" ");
    helper.words = [];
    for (i = 0; i < passageWords.length; i++) {
        helper.words.push({"wordId": `1-1-${i}`, "word": passageWords[i]});
    }
    for(let i = 0;i < helper.questions.length; i++) {
        helper.questions[i].references = helper.questions[i].references.map((ref,index) => {
            return {referId : `reference-${referenceCount++}`,...ref};
        });
    }
    console.log(helper)

}

function delRef() {
    if (!helper.selectedRefId) {
        alert("No reference is selected");
        return;
    }
    document.getElementById(helper.selectedRefId).remove();
   let referenceElements = document.getElementsByClassName(helper.selectedRefId);

    while(referenceElements.length > 0) {
       element = referenceElements[0];
        element.className = element.className.replace(`highlight-${helper.selectedQuestion.qno}`,'');
        if(!element.className.includes(`highlight-`)){
            element.classList.remove('highlighted');
        }
        element.classList.remove(helper.selectedRefId);
    }
    helper.selectedRefId = null;
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
            wordByLine.css += ` ${referId} highlighted  highlight-${highlightQno}`;
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
        console.log(highlightedQuestions)
        highlightedQuestions.forEach(question => {
            if (!highlights[question]) {
                highlights[question] = currentWordCount;
            }
        });

        Object.keys(highlights).forEach(question => {
            if (!highlightedQuestions.includes(question)) {
                // console.log(question, highlights[question], currentWordCount - 1);
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
    if (!startIndex || startIndex.length == 0) {
        for (let i = 0; i < wordsByLine.length; i++) {
            getWord(
                undefined, 
                wordsByLine[i],
                false,
                undefined,
                undefined);
        }
    }
    startIndex.forEach((item) => {
        let start_word = item.start;
        let end_word = item.end;
        for (let i = 0; i < wordsByLine.length; i++) {
            var isHighlighted = i >= start_word && i <= end_word;
            getWord(
                item.referId, 
                wordsByLine[i],
                isHighlighted,
                i == start_word ? item.qno : undefined,
                isHighlighted ? item.qno : undefined);
        }
    });
    
    return wordsByLine;
}

function clickRef(element) {
    removeHighlightedQuestion();
    // console.log(element)
    let referId = element.id;
    let questionNo = element.innerText.trim().replace("Q",'');
    helper.questions.forEach((question) => {
          if(question.qno == questionNo){
            document.getElementById("selectedQuestionId").innerText =
            question.qno + ". " + question.description;
            helper.selectedQuestion = question;
            helper.selectedRefId = referId;
            return;
        }
    });
    document.getElementById("modifyRefButton").innerText = "Modify";
}

function removeHighlightedQuestion() {
    let questionElements = document.getElementsByClassName("questionSection");
    for (let i = 0; i < questionElements.length; i++) {
        questionElements[i].classList.remove("highlightSelection");
    }
}

function modifyRef() {
    // console.log("modifyRef ", helper);
    const selectedElements = getSelectedContent();
    if (!selectedElements) {
        alert("No text is selected");
        return;
    }
    let refId = helper.selectedRefId;
    if (!refId && !helper.selectedQuestion) {
        alert("No reference selected.");
        return;
    }
    if(refId) {
        delRef();
    } else {
        refId = referenceCount++;
    }
    selectedElements.forEach((element)=>{
        element.classList.add("highlighted");
        element.classList.add("highlight-" + helper.selectedQuestion.qno);
        element.classList.add(refId)
    });
    let questionElement = document.createElement("span");
    questionElement.innerHTML = 
        `<span id="${refId}" onclick="clickRef(this)">
            <span  class="question-no-style">Q${helper.selectedQuestion.qno} </span>
        </span>`;
    document.getElementById("passage-section").
        insertBefore(questionElement.firstChild, selectedElements[0]);
}

function append_question_box(wordsByLine, references) {
    var structReferences = [];
    references.forEach((item) => {
        let q_no = item.qno;
        item.references.forEach((ref) => {
            structReferences.push({
                qno: q_no,
                referId: ref.referId,
                start: ref.start_word,
                end: ref.end_word,
            });
        });
    });
    structReferences.sort((a, b) => a.start - b.start);
    var html = ``;
    wordsByLine = passageHightlight(structReferences, wordsByLine);
    wordsByLine.forEach((word, wordInde) => {
        html += word.html;
    });
    return `${html}</div>`;
}

function passageHtml(helper) {
    const references = helper.questions
        .map((question,index) => {
            if (question.references == 0) return;
            return { qno: question.qno, references: question.references};
        })
        .filter((reference) => reference);
    // console.log(helper)
    wordsByLine = helper.words.map((word) => {
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


function clickQuestionRef(element) {
    removeHighlightedQuestion();
    if(helper.selectedRefId){
        helper.selectedRefId = null;
    }
    const questionId = element.id;
    // console.log(element)
    helper.questions.forEach((question) => {
        if (question.qno === questionId) {
            document.getElementById("selectedQuestionId").innerHTML =
                question.qno + ". " + question.description;
            helper.selectedQuestion = question;
            element.parentNode.classList.add("highlightSelection");
        }
    });

    document.getElementById("modifyRefButton").innerText = "Add";
}

function questionHtml(helper) {
    return helper.questions
        .map(
            (question) => `
                <div class="questionSection">
                    <div id="${question.qno}" onclick="clickQuestionRef(this)" class="question">
                        <p><strong>Question ${question.qno}:</strong>
                            ${question.description}
                        </p>
                    </div>
                    ${optionHtml(question)}
                </div>`
        )
        .join("");
}

function reRender(helper) {
    const contentDiv = document.getElementById("content");
    let html = `<div id="passage-section" class="section-html">`;
    html += passageHtml(helper);
    html += `<div class="question-html">${questionHtml(helper)}
        </div>`;
    contentDiv.innerHTML = html;
}

function renderContent(helper) {
    // Listen for mouseup event to trigger the function after selection
    document.addEventListener("mouseup", getSelectedContent);
    document.addEventListener("dblclick", getSelectedContent);

    if (!helper) return;
    reRender(helper);
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