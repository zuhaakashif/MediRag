# 🏥 MediRAG — Role-Aware Medical Knowledge Assistant

A production-grade RAG (Retrieval-Augmented Generation) chatbot that adapts its answers based on **who is asking** — doctor, patient, or hospital staff. Built as a portfolio project to demonstrate advanced AI engineering beyond basic RAG implementations.

---

## 🔥 Live Demo

- **Frontend:** [medirag-medical.streamlit.app](https://medirag-medical.streamlit.app)
- **API:** [medirag-medical.up.railway.app/health](https://medirag-medical.up.railway.app/health)

---

## 💡 What Makes This Different

Most RAG chatbots retrieve documents and return answers. MediRAG goes further:

- **Role-based metadata filtering** — retrieval is scoped at the vector level, not just the prompt. A patient query never touches clinical documents.
- **Live FDA drug data** — integrates the OpenFDA API to answer drug questions for any of 100,000+ medications, not just what's in the knowledge base.
- **Per-role LLM prompting** — doctors get ICD codes and clinical terminology, patients get plain language and safety guardrails, staff get protocol references.
- **Emergency escalation** — detects high-risk patient queries (chest pain, overdose) and automatically appends emergency guidance.
- **Admin dashboard** — query logging, confidence metrics, and knowledge gap tracking via a separate Streamlit dashboard.

---

## 🏗️ Architecture

```
User Query
    │
    ▼
Streamlit Frontend (ui.py)
    │  HTTP POST /chat
    ▼
FastAPI Backend (main.py)
    │
    ├── Pinecone Vector DB ──── Role-filtered retrieval
    │   (55 vectors, 3 audiences)
    │
    ├── OpenFDA API ──────────── Live drug label data
    │   (100,000+ drugs, free)
    │
    └── OpenRouter LLM ──────── Response generation
        (Llama 3.3 70B)
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| Backend | FastAPI + Uvicorn |
| Vector DB | Pinecone (Serverless) |
| Embeddings | OpenAI text-embedding-3-small |
| LLM | Meta Llama 3.3 70B via OpenRouter |
| External Data | OpenFDA Drug Label API |
| Deployment | Railway (API) + Streamlit Cloud (UI) |

---

## 👥 Role System

| Role | Access | Language Style |
|---|---|---|
| **Doctor** | Clinical docs + FDA data | Medical terminology, ICD codes |
| **Patient** | Patient-facing docs + FDA data | Plain language, empathetic tone |
| **Staff/Admin** | Operations docs | Protocol language, policy references |

Role filtering happens at the **Pinecone query level** using metadata filters — not just prompt engineering.

---

## 📁 Project Structure

```
medirag/
├── app/
│   ├── main.py          # FastAPI endpoints
│   ├── chains.py        # LangChain RAG pipeline
│   ├── retriever.py     # Pinecone role-filtered retrieval
│   ├── openfda.py       # Live FDA drug data integration
│   ├── prompts.py       # Role-specific system prompts
│   ├── guardrails.py    # Emergency escalation logic
│   └── logger.py        # Query logging to JSONL
├── frontend/
│   └── ui.py            # Streamlit chat interface
├── dashboard/
│   └── admin.py         # Admin metrics dashboard
├── ingestion/
│   └── ingest.py        # Document chunking + Pinecone upsert
├── data/
│   ├── clinical/        # Doctor-facing documents
│   ├── patient_facing/  # Patient-facing documents
│   └── operations/      # Staff/admin documents
├── Procfile             # Railway deployment config
└── requirements.txt
```

---

## 🚀 Local Setup

### Prerequisites
- Python 3.11
- Pinecone account (free tier)
- OpenRouter account (free tier)

### Installation

```bash
git clone https://github.com/zuhaakashif/MediRag.git
cd medirag
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the root:

```env
PINECONE_API_KEY=your_pinecone_key
PINECONE_HOST=https://your-index.svc.pinecone.io
PINECONE_INDEX_NAME=medirag
OPENROUTER_API_KEY=your_openrouter_key
LLM_MODEL=meta-llama/llama-3.3-70b-instruct:free
```

### Ingest Documents

```bash
python ingestion/ingest.py
```

### Run

```bash
.\run.bat
```

This starts:
- FastAPI backend on `http://localhost:8000`
- Streamlit UI on `http://localhost:8501`
- Admin dashboard on `http://localhost:8502`

---

## 🔌 API

### `GET /health`
Returns API status and environment check.

### `POST /chat`
```json
{
  "query": "What is the dosage for naproxen?",
  "role": "doctor"
}
```

Response:
```json
{
  "answer": "Amoxicillin standard adult dosage is...",
  "sources": ["clinical_pharmacology.txt", "OpenFDA (live)"],
  "confidence": "High"
}
```

---

## 📊 Key Features

- **Confidence scoring** — High / Medium / Low based on vector similarity + FDA data availability
- **Source transparency** — every answer shows which documents were used
- **Knowledge gap tracking** — admin dashboard flags low-confidence queries
- **Auto-clearing on role switch** — chat history resets when role changes

---

## 🌐 Deployment

| Service | Platform | URL |
|---|---|---|
| FastAPI Backend | Railway | medirag-medical.up.railway.app |
| Streamlit Frontend | Streamlit Cloud | medirag-medical.streamlit.app |

---

## 📝 License

MIT
