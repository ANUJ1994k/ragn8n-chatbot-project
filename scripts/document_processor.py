import os
import fitz  # PyMuPDF
from sentence_transformers import SentenceTransformer
from chromadb import Client

client = Client()
model = SentenceTransformer("all-MiniLM-L6-v2")

folder = "./data/sample-documents"
for fname in os.listdir(folder):
    path = os.path.join(folder, fname)
    if fname.endswith(".pdf"):
        text = "".join(page.get_text() for page in fitz.open(path))
    else:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
    chunks = [text[i:i+1000] for i in range(0, len(text), 1000)]
    for i, chunk in enumerate(chunks):
        emb = model.encode(chunk)
        client.add(collection="faq", ids=[f"{fname}-{i}"], embeddings=[emb], metadatas=[{"source": fname, "chunk": i, "text": chunk}])