const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const axios = require('axios');

const app = express();
app.use(cors());
app.use(bodyParser.json());

const GEMINI_API_KEY = '請填入你的Gemini API金鑰'; // TODO: 請填入你的金鑰

app.post('/api/gemini', async (req, res) => {
  const { messages } = req.body;
  try {
    const response = await axios.post(
      'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=' + GEMINI_API_KEY,
      {
        contents: [
          {
            role: 'user',
            parts: [{ text: messages.join('\n') }]
          }
        ]
      }
    );
    const text = response.data.candidates?.[0]?.content?.parts?.[0]?.text || '（無回應）';
    res.json({ text });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.listen(3001, () => {
  console.log('Gemini proxy server running on http://localhost:3001');
}); 