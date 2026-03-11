"""
openfda.py
Fetches real FDA drug label data for any drug query.
No API key required — completely free and open.
Works for ANY drug — does not rely on a hardcoded list.
"""

import requests
import re
OPENFDA_URL = "https://api.fda.gov/drug/label.json"
OPENFDA_API_KEY = "https://api.fda.gov/drug/event.json?api_key=7CRk9FC2SKTr9qnqPypRG3gGrMmtu4PBdPN3UwqV"

DRUG_QUERY_KEYWORDS = [
    "drug", "medication", "medicine", "tablet", "capsule", "pill",
    "dosage", "dose", "mg", "side effect", "interaction", "contraindication",
    "overdose", "prescription", "antibiotic", "painkiller", "injection",
    "what is", "how much", "can i take", "safe to take", "used for",
    "treat", "warning", "adverse", "brand name", "generic", "how do i take",
    "dosage for", "dose for", "side effects of", "information on",
]

def is_drug_query(query: str) -> bool:
    q = query.lower()
    return any(kw in q for kw in DRUG_QUERY_KEYWORDS)

def extract_drug_name(query: str) -> str:
    """
    Extract just the drug name from a natural language query.
    Strategy: remove all known question phrases, what's left is the drug name.
    """
    q = query.lower().strip()

    # Remove question phrases — order matters, longest first
    phrases = sorted([
        "what is the dosage for", "what are the side effects of",
        "what is the dose of", "what is the dose for",
        "what are the contraindications of", "what are the contraindications for",
        "what are the interactions of", "what are the interactions for",
        "what are the warnings for", "what are the adverse effects of",
        "tell me about", "how do i take", "can i take",
        "is it safe to take", "what is", "how much of", "how much",
        "interactions for", "contraindications for", "warnings for",
        "what are the uses of", "what does", "do for",
        "dosage for", "dose for", "side effects of",
        "information on", "info on", "about",
        "effects of", "uses of", "use of",
    ], key=len, reverse=True)

    for phrase in phrases:
        q = q.replace(phrase, "")

    # Remove age/demographic qualifiers
    q = re.sub(r"for (a |an )?\d+[\s\-]year[\s\-]old (\w+)?", "", q)
    q = re.sub(r"for (adults?|children|kids?|elderly|pregnant women?|infants?|babies?)", "", q)
    q = re.sub(r"in (adults?|children|kids?|elderly|pregnant women?)", "", q)

    # Remove trailing/leading punctuation and whitespace
    q = re.sub(r"[?.,!;:]", "", q).strip()

    # If multiple words remain, take the last meaningful word or two
    # (e.g. "the drug panadol" → "panadol")
    words = [w for w in q.split() if w not in ("the", "a", "an", "of", "for", "is", "are", "drug", "medicine", "medication")]
    if words:
        # Return last 1-2 words (the actual drug name)
        return " ".join(words[-2:]) if len(words) >= 2 else words[-1]

    return q.strip()

def search_fda(drug_name: str) -> dict | None:
    """
    Try multiple search strategies to find the drug in OpenFDA.
    Returns the first label found, or None.
    """
    strategies = [
        f'openfda.generic_name:"{drug_name}"',
        f'openfda.brand_name:"{drug_name}"',
        f'openfda.substance_name:"{drug_name}"',
        f'openfda.generic_name:{drug_name}',
        f'openfda.brand_name:{drug_name}',
        drug_name,  # broad full-text fallback
    ]

    for strategy in strategies:
        try:
            r = requests.get(
                OPENFDA_API_KEY,
                params={"search": strategy, "limit": 1},
                timeout=8
            )
            if r.status_code == 200:
                results = r.json().get("results", [])
                if results:
                    print(f"  ✅ OpenFDA found '{drug_name}' via: {strategy[:60]}")
                    return results[0]
        except Exception as e:
            print(f"  ⚠️  OpenFDA search error: {e}")
            continue

    print(f"  ❌ OpenFDA: no results for '{drug_name}'")
    return None

def get_field(label: dict, *fields) -> str | None:
    for field in fields:
        val = label.get(field, [])
        if val and str(val[0]).strip():
            return str(val[0])[:1500].strip()
    return None

def fetch_fda_data(drug_name: str, role: str) -> str | None:
    label = search_fda(drug_name)
    if not label:
        return None

    brand   = label.get("openfda", {}).get("brand_name",   [drug_name.title()])
    generic = label.get("openfda", {}).get("generic_name", [])

    if role == "doctor":
        sections = [
            ("DRUG NAME",         ", ".join(brand)),
            ("GENERIC NAME",      ", ".join(generic) if generic else None),
            ("INDICATIONS",       get_field(label, "indications_and_usage", "purpose")),
            ("DOSAGE & ADMIN",    get_field(label, "dosage_and_administration")),
            ("CONTRAINDICATIONS", get_field(label, "contraindications")),
            ("WARNINGS",          get_field(label, "warnings_and_cautions", "warnings", "boxed_warning")),
            ("DRUG INTERACTIONS", get_field(label, "drug_interactions")),
            ("ADVERSE REACTIONS", get_field(label, "adverse_reactions")),
            ("PREGNANCY",         get_field(label, "pregnancy", "pregnancy_or_breast_feeding")),
            ("PEDIATRIC USE",     get_field(label, "pediatric_use")),
            ("MECHANISM",         get_field(label, "mechanism_of_action", "clinical_pharmacology")),
        ]
    elif role == "patient":
        sections = [
            ("MEDICINE NAME",     ", ".join(brand)),
            ("ALSO KNOWN AS",     ", ".join(generic) if generic else None),
            ("WHAT IT TREATS",    get_field(label, "purpose", "indications_and_usage")),
            ("HOW TO TAKE IT",    get_field(label, "dosage_and_administration", "directions")),
            ("DO NOT USE IF",     get_field(label, "contraindications", "do_not_use")),
            ("WARNINGS",          get_field(label, "warnings", "warnings_and_cautions")),
            ("SIDE EFFECTS",      get_field(label, "adverse_reactions", "stop_use")),
            ("ASK DOCTOR BEFORE", get_field(label, "ask_doctor", "ask_doctor_or_pharmacist")),
        ]
    else:  # staff
        sections = [
            ("DRUG NAME",   ", ".join(brand)),
            ("GENERIC",     ", ".join(generic) if generic else None),
            ("INDICATIONS", get_field(label, "indications_and_usage", "purpose")),
            ("DOSAGE",      get_field(label, "dosage_and_administration")),
            ("WARNINGS",    get_field(label, "warnings", "warnings_and_cautions")),
            ("STORAGE",     get_field(label, "storage_and_handling", "how_supplied")),
        ]

    lines = ["[FDA DRUG LABEL — Source: OpenFDA Live Database]\n"]
    for key, val in sections:
        if val:
            lines.append(f"{key}:\n{val}\n")

    return "\n".join(lines) if len(lines) > 1 else None


def get_fda_context(query: str, role: str) -> str | None:
    """Main entry point — checks query, extracts drug name, fetches FDA data."""
    if not is_drug_query(query):
        return None

    drug_name = extract_drug_name(query)
    if not drug_name or len(drug_name) < 2:
        return None

    print(f"  💊 OpenFDA lookup: extracted='{drug_name}' from query='{query[:50]}'")
    return fetch_fda_data(drug_name, role)
