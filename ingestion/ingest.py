"""
ingest.py — Phase 2 (updated)
Clears existing vectors per folder before re-ingesting.
Run: python ingestion/ingest.py
"""

import os, time, uuid
from pathlib import Path
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI

load_dotenv()

PINECONE_API_KEY   = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX     = os.getenv("PINECONE_INDEX_NAME", "medirag")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
EMBED_MODEL        = "text-embedding-3-small"
CHUNK_SIZE         = 500
CHUNK_OVERLAP      = 100

FOLDER_AUDIENCE = {
    "clinical":       "doctor",
    "patient_facing": "patient",
    "operations":     "staff",
}
FOLDER_SENSITIVITY = {
    "clinical":       "high",
    "patient_facing": "low",
    "operations":     "medium",
}

client = OpenAI(api_key=OPENROUTER_API_KEY, base_url="https://openrouter.ai/api/v1")

def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    chunks, start = [], 0
    while start < len(text):
        chunk = text[start:start + chunk_size].strip()
        if chunk:
            chunks.append(chunk)
        start += chunk_size - overlap
    return chunks

def embed_texts(texts):
    print(f"  Embedding {len(texts)} chunks...")
    response = client.embeddings.create(model=EMBED_MODEL, input=texts)
    return [item.embedding for item in response.data]

def get_or_create_index(pc, index_name):
    existing = [idx.name for idx in pc.list_indexes()]
    if index_name in existing:
        print(f"✅ Index '{index_name}' exists.")
        return
    print(f"Creating index '{index_name}'...")
    pc.create_index(
        name=index_name, dimension=1536, metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )
    print("Waiting for index", end="")
    while not pc.describe_index(index_name).status["ready"]:
        print(".", end="", flush=True)
        time.sleep(2)
    print("\n✅ Index ready.")

def delete_vectors_by_folder(index, folder):
    """Delete all existing vectors for a folder using metadata filter."""
    try:
        index.delete(filter={"folder": {"$eq": folder}})
        print(f"  🗑️  Cleared old vectors for folder='{folder}'")
    except Exception as e:
        print(f"  ⚠️  Could not clear old vectors: {e}")

def ingest_documents(data_dir="data"):
    print("\n🏥 MediRAG — Document Ingestion Pipeline")
    print("=" * 45)

    pc = Pinecone(api_key=PINECONE_API_KEY)
    get_or_create_index(pc, PINECONE_INDEX)
    index = pc.Index(PINECONE_INDEX)

    total_vectors = 0

    for folder, audience in FOLDER_AUDIENCE.items():
        folder_path = Path(data_dir) / folder
        if not folder_path.exists():
            print(f"⚠️  Folder not found: {folder_path} — skipping")
            continue

        txt_files = [f for f in folder_path.glob("*.txt") if f.name != "README.txt"]
        if not txt_files:
            print(f"⚠️  No .txt files in {folder_path} — skipping")
            continue

        print(f"\n📁 Processing: {folder}/ (audience={audience})")

        # Clear old vectors for this folder first
        delete_vectors_by_folder(index, folder)
        time.sleep(1)  # Let delete propagate

        for file_path in txt_files:
            print(f"  📄 {file_path.name}")
            text   = file_path.read_text(encoding="utf-8")
            chunks = chunk_text(text)
            print(f"  → {len(chunks)} chunks")
            if not chunks:
                continue

            embeddings = embed_texts(chunks)

            vectors = []
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                vectors.append({
                    "id":     f"{folder}-{file_path.stem}-{i}-{uuid.uuid4().hex[:8]}",
                    "values": embedding,
                    "metadata": {
                        "text":        chunk,
                        "source":      file_path.name,
                        "audience":    audience,
                        "sensitivity": FOLDER_SENSITIVITY[folder],
                        "chunk_index": i,
                        "folder":      folder,
                    }
                })

            for i in range(0, len(vectors), 100):
                batch = vectors[i:i+100]
                index.upsert(vectors=batch)
                print(f"  ✅ Upserted batch {i//100+1} ({len(batch)} vectors)")

            total_vectors += len(vectors)

    print(f"\n{'='*45}")
    print(f"✅ Ingestion complete! Total vectors: {total_vectors}")
    print(f"📊 {index.describe_index_stats()}")

if __name__ == "__main__":
    ingest_documents("data")
