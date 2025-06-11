from fastapi import FastAPI, Request
from pydantic import BaseModel
import chromadb
from sentence_transformers import SentenceTransformer
import os

app = FastAPI()
client = chromadb.Client()
collection = client.get_or_create_collection(name="faq")
model = SentenceTransformer("all-MiniLM-L6-v2")

class QueryInput(BaseModel):
    query: str

@app.post("/search")
def search(q: QueryInput):
    results = collection.query(query_texts=[q.query], n_results=5, include=["documents", "metadatas", "distances"])
    return {"chunks": results["metadatas"][0], "scores": results["distances"][0]}
