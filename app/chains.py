"""
chains.py — updated
Merges Pinecone retrieval with live OpenFDA drug data.
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from app.retriever import retrieve
from app.prompts import get_prompt
from app.guardrails import check_escalation
from app.openfda import get_fda_context

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
LLM_MODEL          = os.getenv("LLM_MODEL", "meta-llama/llama-3.3-70b-instruct:free")

def get_llm():
    return ChatOpenAI(
        api_key=OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1",
        model=LLM_MODEL,
        temperature=0.2,
    )

def build_pinecone_context(chunks):
    if not chunks:
        return ""
    parts = []
    for i, chunk in enumerate(chunks):
        parts.append(f"[Internal Doc {i+1}: {chunk['source']}]\n{chunk['text']}")
    return "\n\n---\n\n".join(parts)

def run_chain(query: str, role: str) -> dict:
    # ── Retrieve ──────────────────────────────────────────────────────────
    chunks = retrieve(query, role, top_k=4)
    pinecone_context = build_pinecone_context(chunks)
    fda_context      = get_fda_context(query, role)

    # ── Build merged context ──────────────────────────────────────────────
    context_parts = []
    if fda_context:
        context_parts.append("=== FDA DRUG LABEL DATA (use this as your primary source for drug info) ===\n" + fda_context)
    if pinecone_context:
        context_parts.append("=== INTERNAL KNOWLEDGE BASE ===\n" + pinecone_context)

    context = "\n\n".join(context_parts) if context_parts else "No relevant information found."

    # ── LLM call ──────────────────────────────────────────────────────────
    system_prompt = get_prompt(role)
    llm = get_llm()

    user_message = f"""You have been provided with context below. Answer the question using the information in the context.

IMPORTANT RULES:
- If FDA Drug Label Data is present, USE IT to answer drug-related questions. Do not say the context is missing information if FDA data is present.
- Be specific — extract exact dosages, interactions, warnings from the context.
- If genuinely no relevant info exists in any context section, only then say so.

CONTEXT:
{context}

QUESTION: {query}

Answer:"""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_message)
    ]

    response = llm.invoke(messages)
    answer   = response.content.strip()

    # ── Guardrails ────────────────────────────────────────────────────────
    escalation = check_escalation(query, role)
    if escalation and escalation not in answer:
        answer = f"{answer}\n\n{escalation}"

    # ── Confidence ────────────────────────────────────────────────────────
    has_fda   = fda_context is not None
    top_score = chunks[0]["score"] if chunks else 0

    if has_fda and top_score >= 0.45:
        confidence = "High"
    elif has_fda or top_score >= 0.5:
        confidence = "Medium"
    else:
        confidence = "Low — answer may be incomplete"

    sources = list(dict.fromkeys([c["source"] for c in chunks]))
    if has_fda:
        sources.append("OpenFDA (live)")

    return {
        "answer":     answer,
        "sources":    sources,
        "confidence": confidence,
        "chunks":     chunks,
    }
