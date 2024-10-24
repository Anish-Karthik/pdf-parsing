var helper = {};
var data = [];
var referenceCount = 0;
var uploadedFileName = "data.json";
function downloadJSONFile(data, filename = uploadedFileName) {
    populateDataFromHtml();
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
    uploadedFileName = file.name;
    if (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
            try {
                const jsonData = JSON.parse(e.target.result);
                data = jsonData;
                helper = structuredClone(data);
                preprocessData();
                console.log("preprocess data", data)
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
        //    console.log(passageWords[i],i)
        if (passageWords[i].trim() === "") {
            continue;
        }
        helper.words.push({ "wordId": `1-1-${i}`, "word": passageWords[i] });
    }
    for (let i = 0; i < helper.questions.length; i++) {
        helper.questions[i].references = helper.questions[i].references.map((ref, index) => {
            return { referId: `reference-${referenceCount++}`, ...ref };
        });
    }
    // console.log(helper)
}

function delRef() {
    if (helper.selectedOption != null) {
        optionRef = "option-ref-" + helper.selectedQuestion.qno + "-" + helper.selectedOption;
        let existingRef = document.getElementsByClassName(optionRef);
        while (existingRef.length > 0) {
            existingRef[0].classList.remove(optionRef, "highlightOptionRef");
        }
        return;
    }
    if (!helper.selectedRefId) {
        alert("No reference is selected");
        return;
    }
    document.getElementById(helper.selectedRefId).remove();
    let referenceElements = document.getElementsByClassName(helper.selectedRefId);

    while (referenceElements.length > 0) {
        element = referenceElements[0];
        element.className = element.className.replace(`highlight-${helper.selectedQuestion.qno}`, '');
        if (!element.className.includes(`highlight-`)) {
            element.classList.remove('highlighted');
        }
        element.classList.remove(helper.selectedRefId);
    }
}
function delRefAction() {
    delRef();
    resetHelper();
}
function getWord(referId, wordByLine, isHighlighted, questionNo, highlightQno) {
    let isTabbed = false;
    let isLineBreak = false;
    if (wordByLine.word.startsWith("\n\t")) {
        isTabbed = true;
        isLineBreak = true;
    }
    if (wordByLine.word.startsWith("\n")) {
        isLineBreak = true;
    }
    if (isHighlighted) {
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
                <span class="passage-word ${isTabbed ? "tab" : ""} ${isLineBreak ? "new-line" : ""} ${wordByLine.css}" id='${wordByLine.wordId}'> 
                    ${wordByLine.word}
                </span>`;
    if (isLineBreak) {
        wordByLine.html = "<br/>" + wordByLine.html;
    }
}
function populateOption() {
    data.questions.forEach((question, qnInd) => {
        question.options.forEach((option, opInd) => {
            option.reference = null;
        })
    })
    let wordElements = document.getElementsByClassName("passage-word");
    let currentWordCount = 0;
    let highlights = {};
    for (let i = 0; i < wordElements.length; i++) {
        let wordElement = wordElements[i];
        let txt = wordElement.innerText;
        if (txt.trim().length === 0) {
            continue;
        }
        let cssClasses = wordElement.getAttribute("class").split(" ");
        let questionNumber;
        let optionNumber;
        cssClasses.forEach(cssClass => {
            if (cssClass.startsWith("option-ref-")) {
                let clsSplit = cssClass.replace("option-ref-", "").split("-");
                questionNumber = clsSplit[0];
                optionNumber = clsSplit[1];
            }
        });
        if (questionNumber) {
            let ref = questionNumber + "-" + optionNumber;
            if (highlights[ref] === undefined) {
                highlights[ref] = {};
            }
            if (highlights[ref]["start_word"] === undefined) {
                highlights[ref]["start_word"] = currentWordCount;
            }
            highlights[ref]["end_word"] = currentWordCount;
        }
        currentWordCount += wordElement.innerText.trim().split(" ").length;
    }
    console.log(highlights)
    Object.keys(highlights).forEach(optRef => {
        let splitRef = optRef.split("-")
        let qno = parseInt(splitRef[0])
        let optionNo = splitRef[1]
        data.questions[qno - parseInt(helper.questions[0].qno)].options[optionNo].reference = {
            start_word: highlights[optRef].start_word,
            end_word: highlights[optRef].end_word
        }
    });
    console.log(highlights)
}

function populateDataFromHtml() {
    let wordElements = document.getElementsByClassName("passage-word");
    let questionElements = document.getElementsByClassName("question");
    let currentWordCount = 0;
    let highlights = {};
    let passage = "";
    data.questions.forEach(question => {
        question.references = [];
    });
    data.header = document.getElementById("passage-header").innerText;
    for (let i = 0; i < questionElements.length; i++) {
        data.questions[i].description = questionElements[i].childNodes[1].childNodes[1].textContent.trim();

        let optionElements = document.getElementsByClassName("option-" + (i + 1));
        console.log(optionElements);
        for (let j = 0; j < optionElements.length; j++) {
            if (optionElements[j].className.split(" ").includes("correct-option")) {
                data.questions[i].correct_option = String.fromCharCode(65 + j);;
            }
            data.questions[i].options[j].description = optionElements[j].childNodes[2].textContent.trim()
        }
    }
    const referenceMap = new Map();
    for (let i = 0; i < wordElements.length; i++) {
        let wordElement = wordElements[i];
        let txt = "";
        let cssClasses = wordElement.getAttribute("class").split(" ");
        cssClasses.forEach((cls) => {
            if (cls.startsWith("reference-")) {
                var refData = cls.split("-");
                var qnNo = refData[refData.length - 1];
                if (!referenceMap.has(cls)) {
                    referenceMap.set(cls, "");
                    txt += "QS$$" + (parseInt(qnNo) - parseInt(helper.questions[0].qno)) + " ";
                }
            }
            referenceMap.forEach((value, key) => {
                if (!cssClasses.includes(key)) {
                    var refData = key.split("-");
                    var qnNo = refData[refData.length - 1];
                    txt += "QE$$" + (parseInt(qnNo) - parseInt(helper.questions[0].qno)) + " ";
                    referenceMap.delete(key);
                }
            })
        })
        txt += wordElement.innerText.replace(/\s+/g, ' ').trim();
        if (txt.length === 0) {
            continue;
        }
        if (wordElement.className.includes("tab")) {
            txt = "\t" + txt;
        }
        if (wordElement.className.includes("new-line")) {
            txt = "\n" + txt;
        }
        passage += " " + txt;
    }
    data.passage = passage;
    populateOption();
    console.log(data)
}

function passageHightlight(wordsByLine) {
    const questionMap = new Map();
    var refId = 0;
    var prev = "";
    console.log("words by line: " + wordsByLine);
    wordsByLine.forEach((word, index) => {
        var wordText = word.word.trim();
        if (wordText.startsWith("QS$$")) {
            let qno = parseInt(wordText.replace("QS$$", ""));
            if (!questionMap.has(qno)) {
                questionMap.set(qno, { freq: 1, refId: refId++ });
            } else {
                questionMap.set(qno, { freq: questionMap.get(qno).freq + 1, refId: questionMap.get(qno).refId });
            }
        } else if (wordText.startsWith("QE$$")) {
            let qno = parseInt(wordText.replace("QE$$", ""));
            if (questionMap.get(qno).freq > 0) {
                questionMap.set(qno, { freq: questionMap.get(qno).freq - 1, refId: questionMap.get(qno).refId });
            }
            if (questionMap.get(qno).freq === 0) {
                questionMap.delete(qno);
            }
        } else {
            if (questionMap.size > 0) {
                questionMap.forEach((value, key) => {
                    console.log("key :" + key)
                    getWord(
                        "reference-" + (value.refId) + "-" + (parseInt(key) + parseInt(helper.questions[0].qno)),
                        wordsByLine[index],
                        true,
                        prev.startsWith("QS$$" + (key)) && value.freq == 1 ? parseInt(key) + parseInt(helper.questions[0].qno) : undefined,
                        parseInt(key) + parseInt(helper.questions[0].qno));
                })
            }
            else {
                getWord(
                    undefined,
                    wordsByLine[index],
                    false,
                    prev.startsWith("QS$$") ? parseInt(key) + parseInt(helper.questions[0].qno) : undefined,
                    undefined);
            }
        }
        prev = wordText;
        console.log(questionMap)
    });

    return wordsByLine;
}

function resetHelper() {
    helper.selectedRefId = null;
    helper.selectedQuestion = null;
    helper.selectedOption = null;
}

function clickRef(element) {
    removeHighlightedQuestion();
    resetHelper();

    // console.log(element)
    let referId = element.id;
    let questionNo = element.innerText.trim().replace("Q", '');
    helper.questions.forEach((question) => {
        if (question.qno == questionNo) {
            document.getElementById("selectedQuestionId").innerText =
                question.qno + ". " + question.description;
            helper.selectedQuestion = question;
            highlight(element.id);
            helper.selectedRefId = referId;
            return;
        }
    });
    document.getElementById("modifyRefButton").innerText = "Modify";
}

function clickOption(element) {
    console.log(element)
    removeHighlightedQuestion();

    resetHelper();

    // console.log(element)
    let optionIndex = element.id.split("-")[1];
    let questionNo = element.id.split("-")[0];
    let optionReference = document.getElementsByClassName(`option-ref-${questionNo}-${optionIndex}`);
    for (let i = 0; i < optionReference.length; i++) {
        optionReference[i].classList.add("highlightOptionRef");
    }
    if (optionReference.length > 0) {
        optionReference[0].scrollIntoView({ behavior: 'smooth' });
    }
    console.log(optionReference)
    helper.questions.forEach((question) => {
        if (question.qno == questionNo) {
            document.getElementById("selectedQuestionId").innerText =
                question.qno + ". " + question.description;
            helper.selectedQuestion = question;
            helper.selectedOption = optionIndex;

            for (let i = 0; i < question.options.length; i++) {
                if (i == optionIndex) {
                    document.getElementById("selectedOption").innerText =
                        "ABCDE".charAt(i) + ". " + question.options[i].description;
                    break;
                }
            }
            return;
        }
    });
    element.classList.add("highlightSelection");
    document.getElementById("modifyRefButton").innerText = "Modify";
}

function removeHighlightedQuestion() {
    let highlightedElements = document.getElementsByClassName("highlightSelection");
    while (highlightedElements.length > 0) {
        highlightedElements[0].classList.remove("highlightSelection");
    }
    highlightedElements = document.getElementsByClassName("highlightOptionRef");
    while (highlightedElements.length > 0) {
        highlightedElements[0].classList.remove("highlightOptionRef");
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
    if (refId) {
        delRef();
    } else {
        refId = "reference-" + (referenceCount++) + "-" + helper.selectedQuestion.qno;
    }
    let optionRef = "";
    //reference delete
    if (helper.selectedOption != null) {
        optionRef = "option-ref-" + helper.selectedQuestion.qno + "-" + helper.selectedOption;
        delRef();
    }
    selectedElements.forEach((element) => {
        if (helper.selectedOption != null) {
            element.classList.add(optionRef);
            element.classList.add("highlightOptionRef");
        } else {
            element.className += " highlighted highlight-" + helper.selectedQuestion.qno + " " + refId;
        }
    });

    if (helper.selectedOption == null) {
        let questionElement = document.createElement("span");
        questionElement.innerHTML =
            `<span id="${refId}" onclick="clickRef(this)">
                <span  class="question-no-style">Q${helper.selectedQuestion.qno} </span>
            </span>`;
        document.getElementById("passage-section").
            insertBefore(questionElement.firstChild, selectedElements[0]);
    }

    resetHelper();
}

function append_question_box(wordsByLine) {
    var html = ``;
    wordsByLine = passageHightlight(wordsByLine);
    wordsByLine.forEach((word, wordInde) => {
        html += word.html;
    });
    return `${html}</div>`;
}

function passageHtml(helper) {
    // console.log(helper)
    wordsByLine = helper.words.map((word) => {
        return { question: ``, css: ``, html: ``, ...word };
    });
    return append_question_box(wordsByLine);
}

function optionHtml(question) {
    return question.options
        .map(
            (option, index) =>
                `<div class="option-parent">
                  <p 
                    id=${question.qno}-${index}
                    class = 'option option-${question.qno}  ${String.fromCharCode(65 + index) == question.correct_option ? "correct-option" : "incorrect-option"}' 
                    style="margin-left:20px;" onclick="clickOption(this);">
                            <span>${String.fromCharCode(65 + index)}.</span> ${option.description} 
                    </p>
                <button class="opt-disable-btn"><i class="fa fa-check" style="color: rgb(52, 168, 83);"></i></button>
                </div>`
        )
        .join("");
}

function highlight(cls, timeout = 500) {
    element = document.getElementsByClassName(cls)
    for (let i = 0; i < element.length; i++) {
        element[i].style.background = "yellow";
    }
    setTimeout(() => {
        for (let i = 0; i < element.length; i++) {
            element[i].style.background = "";
        }
    }, timeout);
}


function clickQuestionRef(element) {
    removeHighlightedQuestion();
    resetHelper();

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
function makeHeader() {
    let selectedElements = getSelectedContent();
    let headerTxt = "";
    selectedElements.forEach((element) => {
        headerTxt += element.textContent.trim() + " ";
    });

    document.getElementById("passage-header").innerText = headerTxt
    selectedElements.forEach((element) => {
        element.remove();
    })
}
function removeText() {
    let selectedElements = getSelectedContent();
    selectedElements.forEach((element) => {
        if (element.classList.contains("passage-word")) {
            element.remove();
        }
    })
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
    html += `<div class="question-html">${questionHtml(helper)}</div>`;
    document.getElementById("passage-header").innerText = !data.header ? '' : data.header;
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
        if (selectedElements[0] === document.getElementsByClassName("passage-word")[0]) {
            document.getElementById("passage-header-btn").style = "display: block;";
        } else {
            document.getElementById("passage-header-btn").style = "display: none;";
        }
        // Log the attributes of selected elements
        return selectedElements;
    } else {
        document.getElementById("selectedContent").innerHTML = "";
    }
}
function editOptionMode() {
    function handleClick(element, event) {
        if (!confirm(`Are you sure you want to change the option to ${element.innerText}`)) return;
        changeCorrectOption(element, event)
    }
    let options = document.getElementsByClassName('option-parent');
    if (document.getElementById('editMode').checked) {
        for (let i = 0; i < options.length; i++) {
            options[i].getElementsByTagName('button')[0].className = 'opt-change-btn'
            options[i].getElementsByTagName('button')[0].removeEventListener("click", function (event) {
                handleClick(options[i].childNodes[1], event);
            });
            options[i].getElementsByTagName('button')[0].addEventListener("click", function (event) {
                handleClick(options[i].childNodes[1], event);
            });
        }
    } else {
        for (let i = 0; i < options.length; i++) {
            options[i].getElementsByTagName('button')[0].className = "opt-disable-btn"
        }
    }
}

function changeCorrectOption(element, event) {
    let regex = /option-\d{1,}/;
    let classes = Array.from(element.classList)
    let matchingIndex = classes.findIndex(className => regex.test(className));
    all_match_options = document.getElementsByClassName(classes[matchingIndex])
    for (let i = 0; i < all_match_options.length; i++) {
        if (Array.from(all_match_options[i].classList).includes(classes[matchingIndex])) {
            all_match_options[i].classList.remove("correct-option");
            all_match_options[i].classList.add("incorrect-option");
        }
    }
    element.classList.remove("incorrect-option")
    element.classList.add("correct-option")
}

function editModeChanged() {
    let optionElements = document.getElementsByClassName("option")
    let passageElements = document.getElementsByClassName("passage-word");
    let questionElements = document.getElementsByClassName("question");
    if (document.getElementById('editMode').checked) {
        document.getElementById('passage-header').setAttribute("contenteditable", "true");
        for (let i = 0; i < passageElements.length; i++) {
            passageElements[i].setAttribute("contenteditable", "true");
        }
        for (let i = 0; i < questionElements.length; i++) {
            questionElements[i].setAttribute("contenteditable", "true");
        }
        for (let i = 0; i < optionElements.length; i++) {
            optionElements[i].setAttribute("contenteditable", "true");
        }
    } else {
        document.getElementById('passage-header').setAttribute("contenteditable", "false");
        for (let i = 0; i < passageElements.length; i++) {
            passageElements[i].setAttribute("contenteditable", "false");
        }
        for (let i = 0; i < questionElements.length; i++) {
            questionElements[i].setAttribute("contenteditable", "false");
        }
        for (let i = 0; i < optionElements.length; i++) {
            optionElements[i].setAttribute("contenteditable", "false");
        }
    }
    editOptionMode();
}