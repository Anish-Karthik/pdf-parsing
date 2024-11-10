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

function render(questions) {
    const contentDiv = document.getElementById("content");
    let html = `<div style="margin-left: 100px; margin-top: 20px">`
    for (i = 0; i < questions.length; i++) {
        let question = questions[i];

        html += `<div>${question.description}</div></br>`;

        for (j = 0; j < question.options.length; j++) {
            let option = question.options[j];
            html += ` <div>${j+1}. ${option}</div>`;
        }



        html += `</br>`

        html += `<div>${question.additional_context}</div>`

        html += `</br><hr></br>`
        
    }
    html += `</div>`
    contentDiv.innerHTML = html;
}