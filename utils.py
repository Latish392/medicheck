"""
utils.py
Shared helper functions for the Streamlit UI.
"""
from symptom_analyzer import TRIAGE_LEVELS


def triage_badge(level: str) -> str:
    """Return the display label for a triage level."""
    return TRIAGE_LEVELS.get(level, TRIAGE_LEVELS["SEE_A_DOCTOR"])["label"]


def triage_color(level: str) -> str:
    """Return the Streamlit color name for st.success / st.warning / st.error."""
    mapping = {
        "SELF_CARE": "success",
        "SEE_A_DOCTOR": "warning",
        "EMERGENCY": "error",
    }
    return mapping.get(level, "warning")


def format_conditions_table(conditions: list) -> list[dict]:
    """Flatten condition objects into a list of dicts for st.dataframe."""
    rows = []
    for c in conditions:
        rows.append(
            {
                "Condition": c.get("name", "—"),
                "Likelihood": c.get("likelihood", "—"),
                "Details": c.get("brief", "—"),
            }
        )
    return rows


SAMPLE_CASES = [
    {
        "label": "Mild cold",
        "symptoms": "Runny nose, mild sore throat, sneezing for 2 days",
        "age": "28",
        "sex": "Female",
        "duration": "2 days",
        "extra": "No fever, vaccinated",
    },
    {
        "label": "Severe chest pain",
        "symptoms": "Sudden crushing chest pain radiating to left arm, sweating, shortness of breath",
        "age": "55",
        "sex": "Male",
        "duration": "30 minutes",
        "extra": "Hypertension, smoker",
    },
    {
        "label": "Persistent headache",
        "symptoms": "Throbbing headache behind eyes, light sensitivity, nausea",
        "age": "34",
        "sex": "Female",
        "duration": "1 day",
        "extra": "History of migraines",
    },
    {
        "label": "High fever in child",
        "symptoms": "High fever (39.5°C), crying, pulling at ear, reduced appetite",
        "age": "3",
        "sex": "Male",
        "duration": "3 days",
        "extra": "No recent travel",
    },
]
