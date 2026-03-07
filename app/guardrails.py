"""
guardrails.py — Phase 3
Escalation logic and safety disclaimers.
Especially important for the patient bot.
"""

# Keywords that trigger escalation disclaimer for patients
PATIENT_ESCALATION_KEYWORDS = [
    "chest pain", "heart attack", "stroke", "can't breathe", "cannot breathe",
    "difficulty breathing", "shortness of breath", "overdose", "suicide",
    "unconscious", "seizure", "severe pain", "emergency", "bleeding heavily",
    "allergic reaction", "anaphylaxis", "passing out", "fainted",
    "high fever", "fever won't go down", "vomiting blood", "coughing blood",
    "dosage", "how much should i take", "how many pills", "can i take more",
]

PATIENT_ESCALATION_MSG = (
    "\n⚠️ **Please consult your doctor or a qualified healthcare professional "
    "for advice specific to your situation. Do not make changes to your "
    "medication or treatment without professional guidance.**"
)

EMERGENCY_KEYWORDS = [
    "chest pain", "heart attack", "stroke", "can't breathe", "cannot breathe",
    "overdose", "unconscious", "seizure", "bleeding heavily", "anaphylaxis",
    "passing out", "fainted", "vomiting blood", "coughing blood",
]

EMERGENCY_MSG = (
    "\n🚨 **If this is a medical emergency, call emergency services (115 / 1122 "
    "in Pakistan, or your local emergency number) immediately. Do not wait.**"
)

def check_escalation(query: str, role: str) -> str | None:
    """
    Returns a disclaimer/escalation message if needed, else None.
    Currently applies escalation logic for patient role only.
    """
    if role != "patient":
        return None

    query_lower = query.lower()

    # Check for emergency keywords first (highest priority)
    for keyword in EMERGENCY_KEYWORDS:
        if keyword in query_lower:
            return EMERGENCY_MSG + PATIENT_ESCALATION_MSG

    # Check for general escalation keywords
    for keyword in PATIENT_ESCALATION_KEYWORDS:
        if keyword in query_lower:
            return PATIENT_ESCALATION_MSG

    # Always add a soft disclaimer for patient role
    return (
        "\n\n*Please consult your doctor or a healthcare professional "
        "for advice specific to your situation.*"
    )
