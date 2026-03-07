"""
retriever.py — updated
Uses Pinecone directly instead of langchain-pinecone.
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

client = OpenAI(api_key=OPENROUTER_API_KEY, base_url="https://openrouter.ai/api/v1")
pc     = Pinecone(api_key=PINECONE_API_KEY)

def embed_query(text: str) -> list[float]:
    response = client.embeddings.create(model=EMBED_MODEL, input=[text])
    return response.data[0].embedding

def retrieve(query: str, role: str, top_k: int = 4) -> list[dict]:
    index        = pc.Index(PINECONE_INDEX)
    query_vector = embed_query(query)
    role_filter  = ROLE_FILTERS.get(role, {})

    results = index.query(
        vector=query_vector,
        top_k=top_k,
        filter=role_filter,
        include_metadata=True
    )

    chunks = []
    for match in results.matches:
        chunks.append({
            "text":   match.metadata.get("text", ""),
            "source": match.metadata.get("source", "unknown"),
            "score":  match.score,
        })

    return chunks
