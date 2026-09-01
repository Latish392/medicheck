# 🩺 MediCheck — AI-Powered Symptom Checker

A Streamlit application that uses **Gemini 2.0 Flash** to assess patient-reported symptoms
and deliver a structured triage recommendation, differential diagnoses, and actionable advice.

---

## Features

| Feature | Details |
|---|---|
| **AI Triage** | Classifies symptoms as Self-Care 🟢, See a Doctor 🟡, or Emergency 🔴 |
| **Differential Diagnoses** | 3–6 possible related conditions with likelihood scores |
| **Clinical Summary** | Empathetic, evidence-based reasoning from Gemini 2.0 Flash |
| **Actionable Advice** | Home-care tips or urgency guidance depending on triage level |
| **Red-Flag Alerts** | Warning signs that should trigger immediate escalation |
| **Sample Cases** | 4 pre-filled demo scenarios for quick testing |
| **Download Report** | Export results as a plain-text file |

---

## Project Structure

```
health monitor/
├── app.py                  # Main Streamlit application
├── symptom_analyzer.py     # Gemini 2.0 Flash AI engine
├── utils.py                # UI helper functions & sample cases
├── requirements.txt        # Python dependencies
├── .streamlit/
│   └── config.toml         # Streamlit theme configuration
└── README.md
```

---

## Setup & Run

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Get a Gemini API Key

Visit [Google AI Studio](https://aistudio.google.com/app/apikey) → **Create API key** (free tier available).

### 3. Run the app

```bash
streamlit run app.py
```

### 4. Enter your API key

Paste your Gemini API key in the **sidebar** when the app opens. It is never stored to disk.

Alternatively, create a `.env` file in the project root:

```
GEMINI_API_KEY=your_key_here
```

---

## Triage Levels

| Level | Colour | Meaning |
|---|---|---|
| **Self-Care** | 🟢 Green | Mild symptoms — rest, fluids, OTC remedies |
| **See a Doctor** | 🟡 Yellow | Warrants a medical appointment within 24–48 h |
| **Emergency** | 🔴 Red | Life-threatening — call 911 / go to ER now |

---

## Medical Disclaimer

> **MediCheck is for informational purposes only.**  
> It does not replace professional medical advice, diagnosis, or treatment.  
> In a life-threatening emergency, call **911** immediately.

---

## Tech Stack

- **Frontend**: [Streamlit](https://streamlit.io/) (pure Python, no HTML/CSS/JS)
- **AI Model**: [Gemini 2.0 Flash](https://deepmind.google/technologies/gemini/) via `google-generativeai`
- **Config**: `python-dotenv` for optional `.env` key loading
