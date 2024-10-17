var helper = {};
var data = [];
var referenceCount = 0;



function handleFileSelect(event) {
    const file = event.target.files[0];

    if (file) {
        const reader = new FileReader();

        reader.onload = function (event) {
            const fileData = event.target.result;
            console.log(fileData);
            const jsonData = JSON.parse(fileData);
            render(jsonData);
        };

        reader.onerror = function(event) {
            console.error('Error reading file:', event.target.error);
        };

        reader.readAsText(file);
    }
}

function render(quiz) {
    const contentDiv = document.getElementById("content");
    let html = `<div>`
    for (i = 0; i < quiz.questions.length; i++) {
        let question = quiz.questions[i];

        html += `<div>${question.description}</div>`;

        for (j = 0; j < question.options.length; j++) {
            let option = question.options[j];
            html += `<div>${option.description}</div>`;
        }

        html += `</br></br>`
        
    }
    html += `</div>`
    contentDiv.innerHTML = html;
}