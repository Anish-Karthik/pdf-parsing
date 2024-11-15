const http = require('http');
const fs = require('fs');
const path = require('path');

// Get list of HTML files
const htmlFiles = fs.readdirSync('html').filter(file => file.endsWith('.html'));
const startPageId = Math.min(...htmlFiles.map(file => parseInt(file.replace('.html', ''))));
const endPageId = Math.max(...htmlFiles.map(file => parseInt(file.replace('.html', ''))));
console.log(`Found ${htmlFiles.length} HTML files`);

const server = http.createServer((req, res) => {
  // Serve static HTML files
  if (req.url.endsWith('.html')) {
    const filePath = path.join('html', path.basename(req.url)); // Sanitize path
    fs.readFile(filePath, (err, content) => {
      if (err) {
        res.writeHead(404);
        res.end('File not found');
        return;
      }
      res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
      res.end(content);
    });
    return;
  }

  // Handle page routes
  if (req.url.startsWith('/page/')) {
    const pageId = parseInt(req.url.split('/')[2]);
    if (isNaN(pageId) || pageId < startPageId || pageId > endPageId) {
      res.writeHead(404);
      res.end('Page not found');
      return;
    }

    const html = `
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="utf-8">
        <style>
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
        <div id="content"></div>
        <div class="nav-buttons">
          <button class="nav-button" ${pageId === startPageId ? 'disabled' : ''} onclick="window.location.href='/page/${pageId > startPageId ? pageId - 1 : startPageId}'">&lt; Previous</button>
          <button class="nav-button" ${pageId === endPageId ? 'disabled' : ''} onclick="window.location.href='/page/${pageId < endPageId ? pageId + 1 : endPageId}'">Next &gt;</button>
        </div>
        <script>
          fetch('/${pageId}.html')
            .then(response => {
              if (!response.ok) throw new Error('Failed to load content');
              return response.text();
            })
            .then(html => {
              document.getElementById('content').innerHTML = html;
            })
            .catch(err => {
              document.getElementById('content').innerHTML = 'Error loading content: ' + err.message;
            });
        </script>
      </body>
      </html>
    `;
    res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
    res.end(html);
    return;
  }

  // Redirect root to first page
  if (req.url === '/') {
    res.writeHead(302, { 'Location': `/page/${startPageId}` });
    res.end();
    return;
  }

  // Handle 404
  res.writeHead(404);
  res.end('Not found');
});

server.listen(3000, () => {
  console.log('Server is running on port 3000');
});