"""
app.py  —  MediCheck: AI-Powered Symptom Checker
Streamlit application powered by Gemini 2.0 Flash.

Run:  streamlit run app.py
"""

import streamlit as st
import pandas as pd
from symptom_analyzer import analyze_symptoms, TRIAGE_LEVELS, AVAILABLE_MODELS, DEFAULT_MODEL
from utils import triage_color, format_conditions_table, SAMPLE_CASES

# ──────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="MediCheck — AI Symptom Checker",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────
# SIDEBAR — API KEY & APP INFO
# ──────────────────────────────────────────────
# ── Resolve API key: Streamlit Cloud secrets → session_state → sidebar input ──
_cloud_key = st.secrets.get("GEMINI_API_KEY", "") if hasattr(st, "secrets") else ""
if _cloud_key and not st.session_state.get("_api_key"):
    st.session_state["_api_key"] = _cloud_key

with st.sidebar:
    st.title("🩺 MediCheck")
    st.caption("AI-Powered Symptom Checker")
    st.divider()

    st.subheader("🔑 Gemini API Key")

    # On Cloud with a secret already set, show locked status instead of input
    if _cloud_key:
        st.success("API key loaded from Cloud secrets ✓", icon="✅")
        api_key_input = ""
    else:
        api_key_input = st.text_input(
            "Paste your Gemini API key",
            type="password",
            placeholder="AIza...",
            help="Get your free key at https://aistudio.google.com/app/apikey",
            key="gemini_api_key",
        )
        if api_key_input:
            st.session_state["_api_key"] = api_key_input
            st.success("API key saved ✓", icon="✅")
        elif st.session_state.get("_api_key"):
            st.success("API key saved ✓", icon="✅")

    st.divider()
    st.subheader("🤖 Model")
    selected_model = st.selectbox(
        "Gemini model",
        options=AVAILABLE_MODELS,
        index=AVAILABLE_MODELS.index(DEFAULT_MODEL),
        help="If you get a 404 error, switch to a different model.",
        key="selected_model",
    )

    st.divider()
    st.subheader("ℹ️ About")
    st.info(
        "MediCheck uses **Gemini 2.0 Flash** to analyse your symptoms and "
        "provide a triage recommendation:\n\n"
        "- 🟢 **Self-Care** — mild, manageable at home\n"
        "- 🟡 **See a Doctor** — needs medical attention\n"
        "- 🔴 **Emergency** — seek care immediately",
        icon="💡",
    )

    st.divider()
    st.subheader("⚠️ Medical Disclaimer")
    st.warning(
        "This tool is for **informational purposes only** and does **not** "
        "replace professional medical advice, diagnosis, or treatment. "
        "In a life-threatening emergency, call **911** immediately.",
        icon="⚠️",
    )

    st.divider()
    st.caption("Powered by Gemini 2.0 Flash · Built with Streamlit")

# ──────────────────────────────────────────────
# MAIN HEADER
# ──────────────────────────────────────────────
st.title("🩺 MediCheck — AI Symptom Checker")
st.markdown(
    "Describe your symptoms below and receive an instant **AI-powered triage recommendation** "
    "along with possible related conditions and actionable advice."
)
st.divider()

# ──────────────────────────────────────────────
# QUICK-FILL SAMPLE CASES
# ──────────────────────────────────────────────
st.subheader("⚡ Quick Fill — Sample Cases")
sample_cols = st.columns(len(SAMPLE_CASES))
selected_sample = None

for idx, (col, case) in enumerate(zip(sample_cols, SAMPLE_CASES)):
    with col:
        if st.button(case["label"], key=f"sample_{idx}", use_container_width=True):
            selected_sample = case

# Persist sample selection across reruns
if selected_sample:
    st.session_state["sample"] = selected_sample

sample = st.session_state.get("sample", {})

st.divider()

# ──────────────────────────────────────────────
# INPUT FORM
# ──────────────────────────────────────────────
st.subheader("📋 Patient Information")

with st.form("symptom_form", clear_on_submit=False):
    symptoms_input = st.text_area(
        "Describe your symptoms *",
        value=sample.get("symptoms", ""),
        height=120,
        placeholder=(
            "e.g. Severe headache behind both eyes, fever 38.5°C, stiff neck, "
            "sensitivity to light for the past 6 hours…"
        ),
        help="Be as specific as possible — include location, severity (1–10), and character of each symptom.",
    )

    col_a, col_b, col_c = st.columns(3)

    with col_a:
        age_input = st.text_input(
            "Age (optional)",
            value=sample.get("age", ""),
            placeholder="e.g. 35",
        )

    with col_b:
        sex_input = st.selectbox(
            "Biological Sex (optional)",
            options=["Prefer not to say", "Male", "Female", "Other"],
            index=["Prefer not to say", "Male", "Female", "Other"].index(
                sample.get("sex", "Prefer not to say")
            )
            if sample.get("sex") in ["Prefer not to say", "Male", "Female", "Other"]
            else 0,
        )

    with col_c:
        duration_input = st.text_input(
            "Duration of symptoms (optional)",
            value=sample.get("duration", ""),
            placeholder="e.g. 3 days",
        )

    extra_input = st.text_area(
        "Additional context (optional)",
        value=sample.get("extra", ""),
        height=80,
        placeholder="Medical history, medications, allergies, recent travel, pregnancy…",
    )

    submitted = st.form_submit_button(
        "🔍 Analyse Symptoms",
        type="primary",
        use_container_width=True,
    )

# ──────────────────────────────────────────────
# ANALYSIS & RESULTS
# ──────────────────────────────────────────────
if submitted:
    if not symptoms_input.strip():
        st.error("Please describe your symptoms before submitting.", icon="🚨")
        st.stop()

    # Use the persisted key from session_state so it survives form reruns
    effective_api_key = st.session_state.get("_api_key", api_key_input).strip()

    if not effective_api_key:
        st.error(
            "A Gemini API key is required. Enter it in the sidebar.",
            icon="🔑",
        )
        st.stop()

    with st.spinner("🤖 Analysing symptoms with Gemini 2.0 Flash…"):
        try:
            result = analyze_symptoms(
                symptoms=symptoms_input,
                age=age_input,
                sex=sex_input,
                duration=duration_input,
                extra=extra_input,
                api_key=effective_api_key,
                model_name=st.session_state.get("selected_model", DEFAULT_MODEL),
            )
        except ValueError as err:
            st.error(str(err), icon="❌")
            st.stop()
        except Exception as err:
            st.error(f"Unexpected error: {err}", icon="❌")
            st.stop()

    # ── Store in session state so results survive widget interaction ──
    st.session_state["result"] = result

# Render stored result (if any)
if "result" in st.session_state:
    result = st.session_state["result"]
    level = result.get("triage_level", "SEE_A_DOCTOR")
    meta = TRIAGE_LEVELS[level]
    color_fn = triage_color(level)

    st.divider()
    st.subheader("📊 Triage Results")

    # ── Triage banner ──
    banner_fn = getattr(st, color_fn)  # st.success / st.warning / st.error
    banner_fn(
        f"**{meta['label']}** — {meta['description']}",
        icon=meta["label"].split()[0],
    )

    # ── Confidence + top metrics row ──
    m1, m2, m3 = st.columns(3)
    m1.metric("Triage Level", meta["label"])
    m2.metric("AI Confidence", result.get("confidence", "—"))
    m3.metric(
        "Possible Conditions",
        len(result.get("possible_conditions", [])),
    )

    st.divider()

    # ── Two-column layout: summary | conditions ──
    left_col, right_col = st.columns([1.1, 0.9], gap="large")

    with left_col:
        st.subheader("🧠 Clinical Summary")
        st.markdown(result.get("summary", "No summary available."))

        st.subheader("📌 Recommended Actions")
        advice = result.get("advice", [])
        if advice:
            for tip in advice:
                st.markdown(f"- {tip}")
        else:
            st.markdown("_No specific advice provided._")

        st.subheader("🚨 Red-Flag Warning Signs")
        red_flags = result.get("red_flags", [])
        if red_flags:
            for flag in red_flags:
                st.markdown(f"- ⚠️ {flag}")
        else:
            st.markdown("_None identified._")

    with right_col:
        st.subheader("🔬 Possible Related Conditions")
        conditions = result.get("possible_conditions", [])

        if conditions:
            # Likelihood colour-coded pills
            for cond in conditions:
                likelihood = cond.get("likelihood", "")
                if likelihood == "High":
                    badge_color = "🔴"
                elif likelihood == "Moderate":
                    badge_color = "🟡"
                else:
                    badge_color = "🟢"

                with st.expander(
                    f"{badge_color} {cond.get('name', '—')}  ·  {likelihood} likelihood"
                ):
                    st.markdown(cond.get("brief", "No details available."))

            # Compact table view
            st.subheader("📋 Conditions at a Glance")
            df = pd.DataFrame(format_conditions_table(conditions))
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No specific conditions identified.")

    st.divider()

    # ── Disclaimer ──
    st.caption(
        f"⚠️ {result.get('disclaimer', 'This is AI-generated information only. Consult a qualified healthcare professional.')}"
    )

    # ── Raw JSON expander for transparency ──
    with st.expander("🔍 View Raw AI Response (JSON)"):
        st.json(result)

    # ── Action buttons ──
    btn_col1, btn_col2, _ = st.columns([1, 1, 3])
    with btn_col1:
        if st.button("🔄 Clear Results", use_container_width=True):
            del st.session_state["result"]
            if "sample" in st.session_state:
                del st.session_state["sample"]
            st.rerun()
    with btn_col2:
        st.download_button(
            label="⬇️ Download Report",
            data=str(result),
            file_name="medicheck_report.txt",
            mime="text/plain",
            use_container_width=True,
        )

# ──────────────────────────────────────────────
# FOOTER (no results state)
# ──────────────────────────────────────────────
if "result" not in st.session_state:
    st.divider()
    st.markdown(
        "<p style='text-align:center; color:grey; font-size:13px;'>"
        "🩺 MediCheck · AI-Powered Triage · Powered by Gemini 2.0 Flash · Built with Streamlit"
        "</p>",
        unsafe_allow_html=True,
    )
