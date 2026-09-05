"""
symptom_analyzer.py
Core AI engine — calls Gemini via the new google-genai SDK.
"""
import os
import json
import re
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

TRIAGE_LEVELS = {
    "SELF_CARE": {
        "label": "🟢 Self-Care",
        "color": "green",
        "description": "Your symptoms appear mild. Home remedies and rest are likely sufficient.",
    },
    "SEE_A_DOCTOR": {
        "label": "🟡 See a Doctor",
        "color": "orange",
        "description": "Your symptoms warrant a medical consultation. Schedule an appointment soon.",
    },
    "EMERGENCY": {
        "label": "🔴 Emergency",
        "color": "red",
        "description": "Your symptoms may be life-threatening. Seek emergency care immediately (call 911).",
    },
}

SYSTEM_PROMPT = """You are MediCheck, an expert AI-powered medical triage assistant.
Your role is to assess patient-reported symptoms and provide:
1. A triage recommendation: SELF_CARE, SEE_A_DOCTOR, or EMERGENCY
2. A list of 3-6 possible related conditions (differential diagnoses)
3. A clear, empathetic clinical summary explaining the reasoning
4. Specific home-care tips (if SELF_CARE) or urgency guidance (if SEE_A_DOCTOR / EMERGENCY)
5. Red-flag warning signs the user should watch for

IMPORTANT RULES:
- Always respond with valid JSON only - no markdown fences, no extra text.
- Be conservative: when in doubt, escalate the triage level.
- Never diagnose definitively - use "possible", "may indicate", "consistent with".
- Always include a medical disclaimer.

JSON schema you MUST follow exactly:
{
  "triage_level": "SELF_CARE | SEE_A_DOCTOR | EMERGENCY",
  "confidence": "Low | Moderate | High",
  "summary": "string",
  "possible_conditions": [
    {"name": "string", "likelihood": "Low | Moderate | High", "brief": "string"}
  ],
  "advice": ["string"],
  "red_flags": ["string"],
  "disclaimer": "string"
}
"""

# Models confirmed working — verified from API
AVAILABLE_MODELS = [
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-2.5-flash",
]

DEFAULT_MODEL = "gemini-3.6-flash"


def _build_user_prompt(symptoms: str, age: str, sex: str, duration: str, extra: str) -> str:
    parts = [f"Symptoms: {symptoms}"]
    if age:
        parts.append(f"Patient age: {age}")
    if sex and sex != "Prefer not to say":
        parts.append(f"Biological sex: {sex}")
    if duration:
        parts.append(f"Duration of symptoms: {duration}")
    if extra:
        parts.append(f"Additional context: {extra}")
    return "\n".join(parts)


def analyze_symptoms(
    symptoms: str,
    age: str = "",
    sex: str = "",
    duration: str = "",
    extra: str = "",
    api_key: str = "",
    model_name: str = DEFAULT_MODEL,
) -> dict:
    """
    Send symptoms to Gemini via google-genai SDK and return a parsed triage dict.
    Raises ValueError if the API key is missing or the response cannot be parsed.
    """
    key = api_key or os.getenv("GEMINI_API_KEY", "")
    if not key:
        raise ValueError("Gemini API key is not set. Please enter it in the sidebar.")
    if not key.startswith("AIza"):
        raise ValueError(
            "Invalid API key. Your key must start with 'AIza'.\n\n"
            "The 'AQ...' token you entered is a Google OAuth token — not a Gemini API key.\n\n"
            "Get the correct key at: https://aistudio.google.com/apikey\n"
            "Click 'Create API key' → copy the key starting with 'AIzaSy...'"
        )

    client = genai.Client(api_key=key)

    user_prompt = _build_user_prompt(symptoms, age, sex, duration, extra)

    response = client.models.generate_content(
        model=model_name,
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.2,
            top_p=0.95,
            max_output_tokens=2048,
        ),
    )

    raw = response.text.strip()

    # Strip markdown code fences if the model adds them despite instructions
    raw = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.MULTILINE)
    raw = re.sub(r"\s*```$", "", raw, flags=re.MULTILINE)

    try:
        result = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Could not parse Gemini response as JSON.\n\nRaw response:\n{raw}"
        ) from exc

    # Validate triage level
    if result.get("triage_level") not in TRIAGE_LEVELS:
        result["triage_level"] = "SEE_A_DOCTOR"

    return result
