import os
from pinecone import Pinecone
from openai import OpenAI

PINECONE_API_KEY   = os.environ.get("PINECONE_API_KEY")
PINECONE_INDEX     = os.environ.get("PINECONE_INDEX_NAME", "medirag")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
EMBED_MODEL        = "text-embedding-3-small"

ROLE_FILTERS = {
    "doctor":  {"audience": {"$in": ["doctor", "all"]}},
    "patient": {"audience": {"$in": ["patient", "all"]}},
    "staff":   {"audience": {"$in": ["staff", "all"]}},
}

def get_clients():
    api_key = os.environ.get("OPENROUTER_API_KEY")
    pc_key  = os.environ.get("PINECONE_API_KEY")
    client  = OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1")
    pc      = Pinecone(api_key=pc_key)
    return client, pc

def embed_query(text: str) -> list[float]:
    client, _ = get_clients()
    response  = client.embeddings.create(model=EMBED_MODEL, input=[text])
    return response.data[0].embedding

def retrieve(query: str, role: str, top_k: int = 4) -> list[dict]:
    client, pc   = get_clients()
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
