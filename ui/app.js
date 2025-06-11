async function sendQuery() {
    const query = document.getElementById("query").value;
    const res = await fetch("http://localhost:5678/webhook/rag-chatbot", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query })
    });
    const data = await res.json();
    document.getElementById("response").innerHTML = `<p>${data.response}</p><small>Sources: ${data.sources.join(", ")}</small>`;
  }
  