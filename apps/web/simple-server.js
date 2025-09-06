const express = require('express');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

// Serve static files
app.use(express.static('public'));

// Simple test page
app.get('/', (req, res) => {
  res.send(`
    <!DOCTYPE html>
    <html lang="ru">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>StoryQR - Test Server</title>
      <style>
        body {
          margin: 0;
          padding: 0;
          font-family: Arial, sans-serif;
          background-color: #f9fafb;
          display: flex;
          align-items: center;
          justify-content: center;
          min-height: 100vh;
        }
        .container {
          max-width: 400px;
          width: 100%;
          background: white;
          border-radius: 8px;
          box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
          padding: 24px;
        }
        h1 {
          font-size: 24px;
          font-weight: bold;
          color: #111827;
          margin-bottom: 16px;
        }
        p {
          color: #6b7280;
          margin-bottom: 16px;
        }
        .status {
          margin-bottom: 24px;
        }
        .status-item {
          display: flex;
          justify-content: space-between;
          margin-bottom: 8px;
        }
        .status-label {
          font-size: 14px;
          color: #6b7280;
        }
        .status-value {
          font-size: 14px;
          font-weight: 500;
        }
        .status-running { color: #059669; }
        .status-production { color: #2563eb; }
        .status-framework { color: #7c3aed; }
        .button {
          width: 100%;
          background-color: #2563eb;
          color: white;
          padding: 8px 16px;
          border-radius: 6px;
          text-decoration: none;
          display: block;
          text-align: center;
          transition: background-color 0.2s;
        }
        .button:hover {
          background-color: #1d4ed8;
        }
      </style>
    </head>
    <body>
      <div class="container">
        <h1>StoryQR Test Server</h1>
        <p>This is a simple test server to verify the application is working.</p>
        <div class="status">
          <div class="status-item">
            <span class="status-label">Status:</span>
            <span class="status-value status-running">Running</span>
          </div>
          <div class="status-item">
            <span class="status-label">Environment:</span>
            <span class="status-value status-production">Production</span>
          </div>
          <div class="status-item">
            <span class="status-label">Framework:</span>
            <span class="status-value status-framework">Express.js</span>
          </div>
          <div class="status-item">
            <span class="status-label">Port:</span>
            <span class="status-value status-production">${PORT}</span>
          </div>
        </div>
        <a href="/api/health" class="button">Check API Health</a>
      </div>
    </body>
    </html>
  `);
});

// Health check endpoint
app.get('/api/health', (req, res) => {
  res.json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    environment: process.env.NODE_ENV || 'development'
  });
});

// API Gateway proxy - simple version
app.get('/api/health', (req, res) => {
  res.json({
    message: 'API Gateway proxy',
    note: 'This is a mock response. In production, this would proxy to the actual API.'
  });
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server running on port ${PORT}`);
  console.log(`Environment: ${process.env.NODE_ENV || 'development'}`);
});
