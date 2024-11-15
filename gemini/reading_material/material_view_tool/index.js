const http = require('http');
const fs = require('fs');
const path = require('path');

// Get list of HTML files
const startPageId = 0;
var endPageId = -1;

const server = http.createServer((req, res) => {
  // Handle page routes
  if (req.url.startsWith('/page/')) {
    const pageId = parseInt(req.url.split('/')[2]);
    const questions = []

    fs.readFile('../../Neet/5.json', 'utf8', (err, data) => {
      if (err) {
        console.error('Error reading file:', err);
        return;
      }

      const jsonData = JSON.parse(data);
      endPageId = jsonData.questions.length;

      if (isNaN(pageId) || pageId < startPageId || pageId > endPageId) {
        res.writeHead(404);
        res.end('Page not found');
        return;
      }

      jsonData.questions.forEach(element => {
        let question = {}
        question.description = element.description;
        element.options.forEach(option => {
          if (option.is_correct) {
            question.answer = option.description;
          }
        });
        question.ncert_content = element.html_with_keywords_ncert;
        question.current_content = element.html_with_keywords;
        questions.push(question);
      });

      const html = `
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="utf-8">
        <style>
          .container {
            display: flex;
          }

          .left-section, .right-section {
            flex: 1;
          }
          .left-section {
            margin-right: 30px;
          }
          .nav-buttons {
            position: fixed;
            bottom: 20px;
            left: 0;
            width: 100%;
            text-align: center;
            background: white;
            padding: 10px 0;
            box-shadow: 0 -2px 5px rgba(0,0,0,0.1);
          }
          .nav-button {
            padding: 10px 20px;
            margin: 0 10px;
            font-size: 16px;
            cursor: pointer;
            min-width: 100px;
            min-height: 50px;
          }
          #content {
            margin-bottom: 80px;
          }
          
        </style>
      </head>
      <body>
        <div id="content">
          <div id="question">
            Question: ${questions[pageId].description}
            </br>
            Answer: ${questions[pageId].answer}
          </div>
          </br>
          <div class="container">
            <div class="left-section">
              ${questions[pageId].ncert_content}
            </div>
            <div class="right-section">
              ${questions[pageId].current_content}
            </div>
          </div>
        </div>

        <div class="nav-buttons">
          <button class="nav-button" ${pageId === startPageId ? 'disabled' : ''} onclick="window.location.href='/page/${pageId > startPageId ? pageId - 1 : startPageId}'">&lt; Previous</button>
          <button class="nav-button" ${pageId === endPageId ? 'disabled' : ''} onclick="window.location.href='/page/${pageId < endPageId ? pageId + 1 : endPageId}'">Next &gt;</button>
        </div>
      </body>
      </html>
    `;
      res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
      res.end(html);
      return;
    });


  }

  // Redirect root to first page
  if (req.url === '/') {
    res.writeHead(302, { 'Location': `/page/${startPageId}` });
    res.end();
    return;
  }

  // Handle 404
  // res.writeHead(404);
  // res.end('Not found');
});

server.listen(3000, () => {
  console.log('Server is running on port 3000');
});