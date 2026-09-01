"""
symptom_analyzer.py
Core AI engine — calls Gemini 2.5 Flash and returns structured triage results.
"""
import os
import json
import re
import google.generativeai as genai
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
2. A list of 3–6 possible related conditions (differential diagnoses)
3. A clear, empathetic clinical summary explaining the reasoning
4. Specific home-care tips (if SELF_CARE) or urgency guidance (if SEE_A_DOCTOR / EMERGENCY)
5. Red-flag warning signs the user should watch for

IMPORTANT RULES:
- Always respond with valid JSON only — no markdown fences, no extra text.
- Be conservative: when in doubt, escalate the triage level.
- Never diagnose definitively — use "possible", "may indicate", "consistent with".
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


# Models available for new API keys (most recent first)
AVAILABLE_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-1.5-flash",
    "gemini-1.5-flash-8b",
]

DEFAULT_MODEL = "gemini-1.5-flash"


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
    Send symptoms to Gemini and return a parsed triage dict.
    Raises ValueError if the API key is missing or the response cannot be parsed.
    """
    key = api_key or os.getenv("GEMINI_API_KEY", "")
    if not key:
        raise ValueError("Gemini API key is not set. Please enter it in the sidebar.")

    genai.configure(api_key=key)
    model = genai.GenerativeModel(
        model_name=model_name,
        system_instruction=SYSTEM_PROMPT,
    )

    user_prompt = _build_user_prompt(symptoms, age, sex, duration, extra)

    response = model.generate_content(
        user_prompt,
        generation_config=genai.types.GenerationConfig(
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
        raise ValueError(f"Could not parse Gemini response as JSON.\n\nRaw response:\n{raw}") from exc

    # Validate triage level
    if result.get("triage_level") not in TRIAGE_LEVELS:
        result["triage_level"] = "SEE_A_DOCTOR"

    return result
