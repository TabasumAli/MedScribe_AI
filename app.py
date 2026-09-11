import streamlit as st
import os
from vision import generate_heatmap, detect_abnormalities
from orchestrator import run_agent
from settings import SUPPORTED_LANGUAGES

# ---------- Page config ----------
st.set_page_config(
    page_title="MedScribe AI",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------- Custom CSS ----------
st.markdown("""
<style>
    /* Global font */
    html, body, [class*="css"] {
        font-family: 'Segoe UI', 'Inter', sans-serif;
    }

    /* Header */
    .main-header {
        background: linear-gradient(90deg, #0f766e 0%, #0891b2 100%);
        padding: 1.2rem 1.5rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 1rem;
    }
    .main-header h1 {
        margin: 0; font-size: 1.8rem; font-weight: 700;
    }
    .main-header p {
        margin: 0.2rem 0 0 0; opacity: 0.9; font-size: 0.95rem;
    }

    /* Card */
    .card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin-bottom: 1rem;
    }

    /* Urgency badges */
    .badge {
        display: inline-block;
        padding: 0.4rem 1rem;
        border-radius: 999px;
        font-weight: 600;
        font-size: 0.95rem;
    }
    .badge-routine  { background: #d1fae5; color: #065f46; }
    .badge-urgent   { background: #fef3c7; color: #92400e; }
    .badge-critical { background: #fee2e2; color: #991b1b; }

    /* Agent trace step */
    .trace-step {
        background: #eef2ff;
        border-left: 4px solid #6366f1;
        padding: 0.6rem 0.9rem;
        border-radius: 6px;
        margin-bottom: 0.5rem;
        font-family: 'Consolas', monospace;
        font-size: 0.9rem;
    }

    /* RTL for Urdu/Arabic */
    .rtl {
        direction: rtl;
        text-align: right;
        font-family: 'Noto Nastaliq Urdu', 'Jameel Noori Nastaleeq', sans-serif;
        font-size: 1.1rem;
        line-height: 2.2;
        background: #f0fdf4;
        padding: 1rem 1.2rem;
        border-radius: 12px;
        border: 1px solid #bbf7d0;
    }
</style>
""", unsafe_allow_html=True)

# ---------- Header ----------
st.markdown("""
<div class="main-header">
    <h1>🩺 MedScribe AI</h1>
    <p>Agentic radiology assistant — detects, explains, reports, translates.</p>
</div>
""", unsafe_allow_html=True)

# ---------- Session state ----------
if "result" not in st.session_state:
    st.session_state.result = None
if "image_path" not in st.session_state:
    st.session_state.image_path = None
if "heatmap" not in st.session_state:
    st.session_state.heatmap = None
if "language" not in st.session_state:
    st.session_state.language = "English"

# ---------- Upload panel (always visible on top) ----------
with st.container():
    col_u1, col_u2, col_u3 = st.columns([2, 1, 1])
    with col_u1:
        uploaded = st.file_uploader("Upload chest X-ray", type=["png", "jpg", "jpeg"])
    with col_u2:
        st.session_state.language = st.selectbox(
            "Patient language", SUPPORTED_LANGUAGES,
            index=SUPPORTED_LANGUAGES.index(st.session_state.language),
        )
    with col_u3:
        st.write("")
        st.write("")
        run = st.button("🚀 Analyze", type="primary", use_container_width=True)

if run and uploaded:
    os.makedirs("outputs", exist_ok=True)
    path = f"outputs/{uploaded.name}"
    with open(path, "wb") as f:
        f.write(uploaded.read())

    with st.spinner("🧠 Agent is reasoning..."):
        result = run_agent(path, st.session_state.language)
        _, img_tensor = detect_abnormalities(path)
        heatmap = generate_heatmap(path, img_tensor)

    st.session_state.result = result
    st.session_state.image_path = path
    st.session_state.heatmap = heatmap

# ---------- Tabs (navbar) ----------
tab_diag, tab_trace, tab_patient, tab_about = st.tabs(
    ["🩺 Diagnosis", "🧠 Agent Trace", "💬 Patient View", "ℹ️ About"]
)

# ============================================================
# TAB 1 — DIAGNOSIS
# ============================================================
with tab_diag:
    if st.session_state.result is None:
        st.info("⬆️ Upload an X-ray and click **Analyze** to begin.")
    else:
        result = st.session_state.result
        language = st.session_state.language

        # Row 1: Scan + Heatmap
        st.subheader("📸 Imaging")
        c1, c2 = st.columns(2)
        c1.image(st.session_state.image_path, caption="Original Scan", use_container_width=True)
        c2.image(st.session_state.heatmap, caption="AI Attention (Grad-CAM)", use_container_width=True)

        # Row 2: Urgency + Findings
        st.subheader("🚨 Urgency")
        urgency = result["urgency"].strip().lower()
        badge_class = {
            "routine": "badge-routine",
            "urgent": "badge-urgent",
            "critical": "badge-critical",
        }.get(urgency, "badge-routine")
        st.markdown(
            f'<span class="badge {badge_class}">{urgency.upper()}</span>',
            unsafe_allow_html=True,
        )
        if result["escalated"]:
            st.error("⚠️ Critical finding — alert escalated to on-call radiologist.")

        # Row 3: Clinical Report
        st.subheader("📋 Clinical Report")
        with st.container():
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.write(result["clinical_report"])
            st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# TAB 2 — AGENT TRACE
# ============================================================
with tab_trace:
    if st.session_state.result is None:
        st.info("No trace yet. Run an analysis first.")
    else:
        result = st.session_state.result
        st.subheader("🧠 Agent Reasoning — Step by Step")
        st.caption("This shows exactly which tools the agent decided to call, in what order, and with what inputs.")

        for i, step in enumerate(result["agent_trace"], 1):
            st.markdown(
                f'<div class="trace-step">'
                f'<b>Step {i}:</b> <code>{step["tool"]}</code>'
                f'</div>',
                unsafe_allow_html=True,
            )
            with st.expander(f"Inputs for step {i}"):
                st.json(step["args"])

        with st.expander("🤖 Final agent message"):
            st.write(result.get("final_message", "—"))

# ============================================================
# TAB 3 — PATIENT VIEW
# ============================================================
with tab_patient:
    if st.session_state.result is None:
        st.info("No patient summary yet. Run an analysis first.")
    else:
        result = st.session_state.result
        language = st.session_state.language

        st.subheader(f"💬 آپ کے نتائج کا خلاصہ — {language}" if language == "Urdu"
                     else f"💬 Your Results — {language}")
        st.caption("A plain-language summary of your scan, written for you.")

        summary = result["patient_summary"]
        if language in ["Urdu", "Arabic", "Persian"]:
            st.markdown(f'<div class="rtl">{summary}</div>', unsafe_allow_html=True)
        else:
            st.success(summary)

# ============================================================
# TAB 4 — ABOUT
# ============================================================
with tab_about:
    st.subheader("ℹ️ About MedScribe AI")

    st.markdown("""
**What it does:** Takes a chest X-ray and produces two reports — a structured clinical
report for the radiologist, and a plain-language summary for the patient in their own language.

**How it works:**
1. A pretrained **DenseNet121** (TorchXRayVision, 18 pathologies) detects abnormalities
2. **Grad-CAM** shows which regions the model focused on
3. An **agentic LLM** (openai/gpt-oss-120b via Groq) decides which tools to call:
   detect → report → assess urgency → escalate if critical → translate for patient

**Tech stack:**
- Frontend: Streamlit
- CV model: TorchXRayVision (`densenet121-res224-all`)
- Explainability: Grad-CAM
- Agent: LangGraph + Groq (`openai/gpt-oss-120b`)
- Language: Python 3.11
    """)

    st.warning("⚠️ **Disclaimer:** This is a proof of concept built for a hackathon. "
               "It is **not a medical device** and must not be used for real clinical diagnosis. "
               "Always consult a qualified radiologist.")