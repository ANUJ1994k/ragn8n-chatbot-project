const fs = require('fs');
const axios = require('axios');

const queries = JSON.parse(fs.readFileSync('./tests/sample-queries.json'));

queries.forEach(async (q) => {
  const res = await axios.post('http://localhost:5678/webhook/rag-chatbot', q);
  console.log(res.data);
});