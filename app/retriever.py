"""
retriever.py — Phase 2
Role-aware Pinecone retrieval with metadata filtering.
"""

import os
from dotenv import load_dotenv
from pinecone import Pinecone
from openai import OpenAI

load_dotenv()

PINECONE_API_KEY   = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX     = os.getenv("PINECONE_INDEX_NAME", "medirag")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
EMBED_MODEL        = "text-embedding-3-small"

ROLE_FILTERS = {
    "doctor":  {"audience": {"$in": ["doctor", "all"]}},
    "patient": {"audience": {"$in": ["patient", "all"]}},
    "staff":   {"audience": {"$in": ["staff", "all"]}},
}

_embed_client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)

_pc = Pinecone(api_key=PINECONE_API_KEY)
_index = None

def _get_index():
    global _index
    if _index is None:
        _index = _pc.Index(PINECONE_INDEX)
    return _index

def embed_query(query: str) -> list:
    response = _embed_client.embeddings.create(model=EMBED_MODEL, input=[query])
    return response.data[0].embedding

def retrieve(query: str, role: str, top_k: int = 5) -> list:
    if role not in ROLE_FILTERS:
        raise ValueError(f"Unknown role: {role}. Must be doctor, patient, or staff.")
    index = _get_index()
    query_embedding = embed_query(query)
    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        filter=ROLE_FILTERS[role],
        include_metadata=True
    )
    chunks = []
    for match in results.matches:
        chunks.append({
            "text":     match.metadata.get("text", ""),
            "source":   match.metadata.get("source", "unknown"),
            "audience": match.metadata.get("audience", ""),
            "score":    round(match.score, 4),
        })
    return chunks

if __name__ == "__main__":
    print("\nMediRAG Retriever — Smoke Test")
    print("=" * 45)
    test_queries = [
        ("What are the drug interactions for ibuprofen?", "doctor"),
        ("What is ibuprofen used for?", "patient"),
        ("What is the medication error reporting process?", "staff"),
    ]
    for query, role in test_queries:
        print(f"\n[{role.upper()}] Query: {query}")
        results = retrieve(query, role, top_k=2)
        for i, r in enumerate(results):
            print(f"  Result {i+1} (score={r['score']}, source={r['source']}):")
            print(f"    {r['text'][:150]}...")
