import os
from fastapi import FastAPI
from pydantic import BaseModel
from app.chains import run_chain
from app.logger import log_query

app = FastAPI()

class ChatRequest(BaseModel):
    query: str
    role:  str

@app.get("/health")
def health():
    return {
        "status": "ok",
        "pinecone_key_set":   bool(os.environ.get("PINECONE_API_KEY")),
        "openrouter_key_set": bool(os.environ.get("OPENROUTER_API_KEY")),
        "llm_model":          os.environ.get("LLM_MODEL", "not set"),
    }

@app.post("/chat")
def chat(req: ChatRequest):
    result = run_chain(req.query, req.role)
    log_query(req.query, req.role, result["answer"])
    return {
        "answer":     result["answer"],
        "sources":    result["sources"],
        "confidence": result["confidence"],
    }