"""
logger.py — Phase 4
Logs every query to a JSONL file for the admin dashboard.
"""

import json
import os
from datetime import datetime

LOG_FILE = "logs/query_log.jsonl"

def log_query(role: str, query: str, answer: str, sources: list, confidence: str):
    os.makedirs("logs", exist_ok=True)
    entry = {
        "timestamp":  datetime.utcnow().isoformat(),
        "role":       role,
        "query":      query,
        "answer":     answer,
        "sources":    sources,
        "confidence": confidence,
    }
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

def load_logs() -> list[dict]:
    if not os.path.exists(LOG_FILE):
        return []
    logs = []
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    logs.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return logs
