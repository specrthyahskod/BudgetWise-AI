const express = require('express');
const cors = require('cors');
const path = require('path');
const net = require('net');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 5000;

const allowedOrigins = [
  'https://budgetwiseai-staff-intranet.netlify.app',
  'http://localhost:3000',
  'http://localhost:5173'
];

app.use(cors({
  origin: (origin, callback) => {
    if (!origin || allowedOrigins.includes(origin)) {
      return callback(null, true);
    }
    return callback(new Error('CORS policy violation'));
  },
  credentials: true
}));

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

app.use(express.static(path.join(__dirname, 'public')));

app.get('/api/health', (req, res) => {
  res.status(200).json({ status: 'OK', timestamp: new Date().toISOString() });
});

// Relay endpoint: Connects Netlify Intranet requests to the Python Socket IDI Server on Port 9999
app.post('/api/verify-reset', (req, res) => {
  const { token, new_password } = req.body;

  if (!token || !new_password) {
    return res.status(400).json({ status: 'FAILED', message: 'Missing token or new password' });
  }

  const client = new net.Socket();
  client.setTimeout(5000);

  client.connect(9999, '127.0.0.1', () => {
    const payload = JSON.stringify({
      action: 'VERIFY_AND_RESET',
      token: token,
      new_password: new_password
    });
    client.write(payload);
  });

  client.on('data', (data) => {
    client.destroy();
    try {
      const response = JSON.parse(data.toString());
      return res.json(response);
    } catch (e) {
      return res.status(500).json({ status: 'ERROR', message: 'Invalid response from socket server' });
    }
  });

  client.on('timeout', () => {
    client.destroy();
    return res.status(504).json({ status: 'FAILED', message: 'Socket IDI Server timed out' });
  });

  client.on('error', (err) => {
    client.destroy();
    return res.status(500).json({ status: 'OFFLINE', message: 'Python Socket IDI Server on port 9999 is offline' });
  });
});

app.use('/api/{*splat}', (req, res) => {
  res.status(404).json({ error: 'API route not found' });
});

app.get('{*splat}', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'), (err) => {
    if (err) {
      res.status(404).send('Resource not found');
    }
  });
});

app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ error: 'Internal Server Error' });
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});