const axios = require('axios');

async function searchVectorDB(query) {
  const res = await axios.post('http://localhost:8000/search', { query });
  return [{ json: { context: res.data.chunks, scores: res.data.scores, query } }];
}

async function generateResponse(input) {
  const prompt = `Answer the question using the following context:\n${input.context.map(c => c.text).join("\n\n")}`;
  const res = await axios.post('https://api.openai.com/v1/chat/completions', {
    model: 'gpt-3.5-turbo',
    messages: [{ role: 'user', content: prompt }]
  }, {
    headers: { 'Authorization': `Bearer ${process.env.OPENAI_API_KEY}` }
  });
  return [{ json: { response: res.data.choices[0].message.content, sources: input.context.map(c => c.source) } }];
}

module.exports = { searchVectorDB, generateResponse };