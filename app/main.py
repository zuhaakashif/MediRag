"""
main.py — Phase 4
FastAPI with logging on every /chat request.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(
    title="MediRAG API",
    description="Role-Aware Medical Knowledge Assistant",
    version="0.4.0"
)

VALID_ROLES = ["doctor", "patient", "staff"]

class ChatRequest(BaseModel):
    query: str
    role: str

class ChatResponse(BaseModel):
    answer: str
    role: str
    sources: list
    confidence: str

@app.get("/")
def root():
    return {"status": "MediRAG API is running", "version": "0.4.0"}

@app.get("/health")
def health():
    return {
        "status": "ok",
        "pinecone_configured": bool(os.getenv("PINECONE_API_KEY")),
        "llm_configured":      bool(os.getenv("OPENROUTER_API_KEY")),
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    if req.role not in VALID_ROLES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid role '{req.role}'. Must be one of: {VALID_ROLES}"
        )
    try:
        from app.chains import run_chain
        from app.logger import log_query
        result = run_chain(req.query, req.role)
        log_query(
            role=req.role,
            query=req.query,
            answer=result["answer"],
            sources=result["sources"],
            confidence=result["confidence"],
        )
        return ChatResponse(
            answer=result["answer"],
            role=req.role,
            sources=result["sources"],
            confidence=result["confidence"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
