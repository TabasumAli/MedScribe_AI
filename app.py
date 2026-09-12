# import streamlit as st
# import os
# from vision import generate_heatmap, detect_abnormalities
# from orchestrator import run_agent
# from settings import SUPPORTED_LANGUAGES

# # ---------- Page config ----------
# st.set_page_config(
#     page_title="MedScribe AI",
#     page_icon="🩺",
#     layout="wide",
#     initial_sidebar_state="collapsed",
# )

# # ---------- Custom CSS ----------
# st.markdown("""
# <style>
#     /* Global font */
#     html, body, [class*="css"] {
#         font-family: 'Segoe UI', 'Inter', sans-serif;
#     }

#     /* Header */
#     .main-header {
#         background: linear-gradient(90deg, #0f766e 0%, #0891b2 100%);
#         padding: 1.2rem 1.5rem;
#         border-radius: 12px;
#         color: white;
#         margin-bottom: 1rem;
#     }
#     .main-header h1 {
#         margin: 0; font-size: 1.8rem; font-weight: 700;
#     }
#     .main-header p {
#         margin: 0.2rem 0 0 0; opacity: 0.9; font-size: 0.95rem;
#     }

#     /* Card */
#     .card {
#         background: #f8fafc;
#         border: 1px solid #e2e8f0;
#         border-radius: 12px;
#         padding: 1rem 1.2rem;
#         margin-bottom: 1rem;
#     }

#     /* Urgency badges */
#     .badge {
#         display: inline-block;
#         padding: 0.4rem 1rem;
#         border-radius: 999px;
#         font-weight: 600;
#         font-size: 0.95rem;
#     }
#     .badge-routine  { background: #d1fae5; color: #065f46; }
#     .badge-urgent   { background: #fef3c7; color: #92400e; }
#     .badge-critical { background: #fee2e2; color: #991b1b; }

#     /* Agent trace step */
#     .trace-step {
#         background: #eef2ff;
#         border-left: 4px solid #6366f1;
#         padding: 0.6rem 0.9rem;
#         border-radius: 6px;
#         margin-bottom: 0.5rem;
#         font-family: 'Consolas', monospace;
#         font-size: 0.9rem;
#     }

#     /* RTL for Urdu/Arabic */
#     .rtl {
#         direction: rtl;
#         text-align: right;
#         font-family: 'Noto Nastaliq Urdu', 'Jameel Noori Nastaleeq', sans-serif;
#         font-size: 1.1rem;
#         line-height: 2.2;
#         background: #f0fdf4;
#         padding: 1rem 1.2rem;
#         border-radius: 12px;
#         border: 1px solid #bbf7d0;
#     }
# </style>
# """, unsafe_allow_html=True)

# # ---------- Header ----------
# st.markdown("""
# <div class="main-header">
#     <h1>🩺 MedScribe AI</h1>
#     <p>Agentic radiology assistant — detects, explains, reports, translates.</p>
# </div>
# """, unsafe_allow_html=True)

# # ---------- Session state ----------
# if "result" not in st.session_state:
#     st.session_state.result = None
# if "image_path" not in st.session_state:
#     st.session_state.image_path = None
# if "heatmap" not in st.session_state:
#     st.session_state.heatmap = None
# if "language" not in st.session_state:
#     st.session_state.language = "English"

# # ---------- Upload panel (always visible on top) ----------
# with st.container():
#     col_u1, col_u2, col_u3 = st.columns([2, 1, 1])
#     with col_u1:
#         uploaded = st.file_uploader("Upload chest X-ray", type=["png", "jpg", "jpeg"])
#     with col_u2:
#         st.session_state.language = st.selectbox(
#             "Patient language", SUPPORTED_LANGUAGES,
#             index=SUPPORTED_LANGUAGES.index(st.session_state.language),
#         )
#     with col_u3:
#         st.write("")
#         st.write("")
#         run = st.button("🚀 Analyze", type="primary", use_container_width=True)

# if run and uploaded:
#     os.makedirs("outputs", exist_ok=True)
#     path = f"outputs/{uploaded.name}"
#     with open(path, "wb") as f:
#         f.write(uploaded.read())

#     with st.spinner("🧠 Agent is reasoning..."):
#         result = run_agent(path, st.session_state.language)
#         _, img_tensor = detect_abnormalities(path)
#         heatmap = generate_heatmap(path, img_tensor)

#     st.session_state.result = result
#     st.session_state.image_path = path
#     st.session_state.heatmap = heatmap

# # ---------- Tabs (navbar) ----------
# tab_diag, tab_trace, tab_patient, tab_about = st.tabs(
#     ["🩺 Diagnosis", "🧠 Agent Trace", "💬 Patient View", "ℹ️ About"]
# )

# # ============================================================
# # TAB 1 — DIAGNOSIS
# # ============================================================
# with tab_diag:
#     if st.session_state.result is None:
#         st.info("⬆️ Upload an X-ray and click **Analyze** to begin.")
#     else:
#         result = st.session_state.result
#         language = st.session_state.language

#         # Row 1: Scan + Heatmap
#         st.subheader("📸 Imaging")
#         c1, c2 = st.columns(2)
#         c1.image(st.session_state.image_path, caption="Original Scan", use_container_width=True)
#         c2.image(st.session_state.heatmap, caption="AI Attention (Grad-CAM)", use_container_width=True)

#         # Row 2: Urgency + Findings
#         st.subheader("🚨 Urgency")
#         urgency = result["urgency"].strip().lower()
#         badge_class = {
#             "routine": "badge-routine",
#             "urgent": "badge-urgent",
#             "critical": "badge-critical",
#         }.get(urgency, "badge-routine")
#         st.markdown(
#             f'<span class="badge {badge_class}">{urgency.upper()}</span>',
#             unsafe_allow_html=True,
#         )
#         if result["escalated"]:
#             st.error("⚠️ Critical finding — alert escalated to on-call radiologist.")

#         # Row 3: Clinical Report
#         st.subheader("📋 Clinical Report")
#         with st.container():
#             st.markdown('<div class="card">', unsafe_allow_html=True)
#             st.write(result["clinical_report"])
#             st.markdown('</div>', unsafe_allow_html=True)

# # ============================================================
# # TAB 2 — AGENT TRACE
# # ============================================================
# with tab_trace:
#     if st.session_state.result is None:
#         st.info("No trace yet. Run an analysis first.")
#     else:
#         result = st.session_state.result
#         st.subheader("🧠 Agent Reasoning — Step by Step")
#         st.caption("This shows exactly which tools the agent decided to call, in what order, and with what inputs.")

#         for i, step in enumerate(result["agent_trace"], 1):
#             st.markdown(
#                 f'<div class="trace-step">'
#                 f'<b>Step {i}:</b> <code>{step["tool"]}</code>'
#                 f'</div>',
#                 unsafe_allow_html=True,
#             )
#             with st.expander(f"Inputs for step {i}"):
#                 st.json(step["args"])

#         with st.expander("🤖 Final agent message"):
#             st.write(result.get("final_message", "—"))

# # ============================================================
# # TAB 3 — PATIENT VIEW
# # ============================================================
# with tab_patient:
#     if st.session_state.result is None:
#         st.info("No patient summary yet. Run an analysis first.")
#     else:
#         result = st.session_state.result
#         language = st.session_state.language

#         st.subheader(f"💬 آپ کے نتائج کا خلاصہ — {language}" if language == "Urdu"
#                      else f"💬 Your Results — {language}")
#         st.caption("A plain-language summary of your scan, written for you.")

#         summary = result["patient_summary"]
#         if language in ["Urdu", "Arabic", "Persian"]:
#             st.markdown(f'<div class="rtl">{summary}</div>', unsafe_allow_html=True)
#         else:
#             st.success(summary)

# # ============================================================
# # TAB 4 — ABOUT
# # ============================================================
# with tab_about:
#     st.subheader("ℹ️ About MedScribe AI")

#     st.markdown("""
# **What it does:** Takes a chest X-ray and produces two reports — a structured clinical
# report for the radiologist, and a plain-language summary for the patient in their own language.

# **How it works:**
# 1. A pretrained **DenseNet121** (TorchXRayVision, 18 pathologies) detects abnormalities
# 2. **Grad-CAM** shows which regions the model focused on
# 3. An **agentic LLM** (openai/gpt-oss-120b via Groq) decides which tools to call:
#    detect → report → assess urgency → escalate if critical → translate for patient

# **Tech stack:**
# - Frontend: Streamlit
# - CV model: TorchXRayVision (`densenet121-res224-all`)
# - Explainability: Grad-CAM
# - Agent: LangGraph + Groq (`openai/gpt-oss-120b`)
# - Language: Python 3.11
#     """)

#     st.warning("⚠️ **Disclaimer:** This is a proof of concept built for a hackathon. "
#                "It is **not a medical device** and must not be used for real clinical diagnosis. "
#                "Always consult a qualified radiologist.")






from __future__ import annotations

import html
import json
import os
import uuid
from pathlib import Path
from typing import Any

import streamlit as st
import streamlit.components.v1 as components

from orchestrator import run_agent
from settings import SUPPORTED_LANGUAGES
from vision import detect_abnormalities, generate_heatmap


# -----------------------------------------------------------------------------
# Page configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="MedScribe AI | Radiology Intelligence",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# -----------------------------------------------------------------------------
# Luxury / royal visual system
# -----------------------------------------------------------------------------
ROYAL_CSS = r"""
<style>
:root {
    --bg-0: #050b14;
    --bg-1: #07111f;
    --bg-2: #0b1728;
    --surface-1: #0d1928;
    --surface-2: #101d30;
    --surface-3: #17263b;
    --line: rgba(151, 169, 191, 0.18);
    --line-strong: rgba(215, 194, 154, 0.30);
    --ivory: #f5f1e8;
    --ivory-soft: #ddd7ca;
    --muted: #9aa8b9;
    --muted-2: #6f7d90;
    --gold: #b79a5b;
    --champagne: #d7c29a;
    --sapphire: #4169a8;
    --sapphire-2: #2f527f;
    --success: #58a889;
    --warning: #c79a54;
    --urgent: #d88155;
    --critical: #c75b64;
    --shadow: 0 20px 70px rgba(0, 0, 0, 0.30);
}

html, body, [class*="css"] {
    font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont,
        "Segoe UI", sans-serif;
}

body {
    color: var(--ivory);
}

.stApp {
    background:
        radial-gradient(circle at 82% 8%, rgba(65, 105, 168, 0.11), transparent 31rem),
        radial-gradient(circle at 17% 72%, rgba(183, 154, 91, 0.055), transparent 29rem),
        linear-gradient(145deg, #050b14 0%, #07111f 43%, #081523 100%);
    color: var(--ivory);
    overflow-x: hidden;
}

.stApp::before,
.stApp::after {
    content: "";
    position: fixed;
    pointer-events: none;
    z-index: 0;
    border-radius: 999px;
    filter: blur(18px);
    opacity: 0.8;
}

.stApp::before {
    width: 34rem;
    height: 34rem;
    right: -15rem;
    top: 9rem;
    background: radial-gradient(circle, rgba(65,105,168,.08), rgba(65,105,168,0) 68%);
    animation: medscribeDriftA 24s ease-in-out infinite alternate;
}

.stApp::after {
    width: 28rem;
    height: 28rem;
    left: -13rem;
    bottom: 2rem;
    background: radial-gradient(circle, rgba(215,194,154,.045), rgba(215,194,154,0) 68%);
    animation: medscribeDriftB 30s ease-in-out infinite alternate;
}

@keyframes medscribeDriftA {
    from { transform: translate3d(0, -12px, 0) scale(1); }
    to   { transform: translate3d(-55px, 50px, 0) scale(1.08); }
}

@keyframes medscribeDriftB {
    from { transform: translate3d(0, 0, 0) scale(1.04); }
    to   { transform: translate3d(70px, -38px, 0) scale(.96); }
}

@keyframes medscribePulse {
    0%, 100% { box-shadow: 0 0 0 0 rgba(88, 168, 137, .28); }
    50% { box-shadow: 0 0 0 7px rgba(88, 168, 137, 0); }
}

@keyframes medscribeLine {
    from { transform: translateX(-110%); }
    to   { transform: translateX(290%); }
}

@keyframes medscribeReveal {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0); }
}

@keyframes medscribeBar {
    from { transform: scaleX(0); }
    to   { transform: scaleX(1); }
}

/* Streamlit chrome */
#MainMenu, footer, header[data-testid="stHeader"] {
    visibility: hidden;
}

[data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stStatusWidget"] {
    display: none !important;
}

.block-container {
    position: relative;
    z-index: 2;
    max-width: 1480px;
    padding-top: 1.1rem;
    padding-bottom: 3.5rem;
}

/* Global typography */
h1, h2, h3, h4, h5, h6, p, label, span, div {
    color: inherit;
}

h1, h2, h3 {
    letter-spacing: -0.025em;
}

p {
    color: var(--muted);
}

/* Grid overlay */
.royal-grid {
    position: fixed;
    inset: 0;
    z-index: 0;
    pointer-events: none;
    opacity: .19;
    background-image:
        linear-gradient(rgba(140,157,180,.035) 1px, transparent 1px),
        linear-gradient(90deg, rgba(140,157,180,.035) 1px, transparent 1px);
    background-size: 62px 62px;
    mask-image: linear-gradient(to bottom, rgba(0,0,0,.6), transparent 88%);
}

/* Top bar */
.ms-topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    padding: .72rem .15rem 1.15rem .15rem;
    border-bottom: 1px solid rgba(215,194,154,.12);
    animation: medscribeReveal .55s ease both;
}

.ms-brand {
    display: flex;
    align-items: center;
    gap: .85rem;
}

.ms-monogram {
    width: 2.55rem;
    height: 2.55rem;
    display: grid;
    place-items: center;
    border: 1px solid rgba(215,194,154,.48);
    background: linear-gradient(145deg, rgba(215,194,154,.08), rgba(65,105,168,.045));
    box-shadow: inset 0 0 0 1px rgba(255,255,255,.012), 0 9px 30px rgba(0,0,0,.20);
    color: var(--champagne);
    font-family: "Iowan Old Style", "Palatino Linotype", Georgia, serif;
    font-size: 1rem;
    letter-spacing: .08em;
}

.ms-brand-name {
    font-family: "Iowan Old Style", "Palatino Linotype", Georgia, serif;
    color: var(--ivory);
    font-size: 1.17rem;
    letter-spacing: .035em;
    line-height: 1.05;
}

.ms-brand-meta {
    margin-top: .22rem;
    color: var(--muted-2);
    font-size: .62rem;
    letter-spacing: .18em;
    text-transform: uppercase;
}

.ms-system {
    display: flex;
    align-items: center;
    gap: .58rem;
    color: #aab6c5;
    font-size: .68rem;
    letter-spacing: .12em;
    text-transform: uppercase;
}

.ms-system-dot {
    width: .48rem;
    height: .48rem;
    border-radius: 50%;
    background: var(--success);
    animation: medscribePulse 2.4s ease-in-out infinite;
}

/* Hero */
.ms-hero {
    position: relative;
    overflow: hidden;
    margin: 1.2rem 0 1.6rem;
    min-height: 23rem;
    display: grid;
    grid-template-columns: minmax(0, 1.25fr) minmax(20rem, .75fr);
    gap: 2rem;
    align-items: center;
    padding: 3.4rem 3.4rem;
    border: 1px solid rgba(215,194,154,.15);
    background:
        linear-gradient(110deg, rgba(13,25,40,.96), rgba(9,19,32,.87)),
        radial-gradient(circle at 80% 25%, rgba(65,105,168,.12), transparent 55%);
    box-shadow: var(--shadow);
    animation: medscribeReveal .7s ease .06s both;
}

.ms-hero::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(215,194,154,.55), transparent);
}

.ms-hero::after {
    content: "";
    position: absolute;
    width: 19rem;
    height: 1px;
    top: 0;
    left: 0;
    background: linear-gradient(90deg, transparent, rgba(245,241,232,.7), transparent);
    animation: medscribeLine 8s linear infinite;
    opacity: .45;
}

.ms-eyebrow,
.ms-section-index,
.ms-mini-label {
    color: var(--champagne);
    font-size: .68rem;
    font-weight: 650;
    letter-spacing: .18em;
    text-transform: uppercase;
}

.ms-hero h1 {
    margin: .7rem 0 1rem;
    max-width: 820px;
    color: var(--ivory);
    font-family: "Iowan Old Style", "Palatino Linotype", Georgia, serif;
    font-size: clamp(3.25rem, 6vw, 6.7rem);
    line-height: .91;
    font-weight: 500;
    letter-spacing: -.055em;
}

.ms-hero h1 .gold {
    color: var(--champagne);
}

.ms-hero-copy {
    max-width: 680px;
    margin: 0;
    color: #9eacbd;
    font-size: .98rem;
    line-height: 1.75;
}

.ms-hero-tags {
    margin-top: 1.7rem;
    display: flex;
    flex-wrap: wrap;
    gap: .6rem;
}

.ms-tag {
    padding: .48rem .7rem;
    border: 1px solid rgba(151,169,191,.15);
    background: rgba(255,255,255,.018);
    color: #a9b4c2;
    font-size: .64rem;
    letter-spacing: .08em;
    text-transform: uppercase;
}

.ms-visual {
    position: relative;
    min-height: 17rem;
    display: grid;
    place-items: center;
}

.ms-orbit {
    position: relative;
    width: min(17rem, 72vw);
    aspect-ratio: 1;
    border: 1px solid rgba(215,194,154,.18);
    border-radius: 50%;
    box-shadow:
        inset 0 0 90px rgba(65,105,168,.055),
        0 0 80px rgba(65,105,168,.045);
}

.ms-orbit::before,
.ms-orbit::after {
    content: "";
    position: absolute;
    border-radius: 50%;
    inset: 14%;
    border: 1px solid rgba(151,169,191,.12);
}

.ms-orbit::after {
    inset: 31%;
    border-color: rgba(215,194,154,.22);
    background: radial-gradient(circle, rgba(215,194,154,.06), rgba(65,105,168,.02), transparent 70%);
}

.ms-cross-h,
.ms-cross-v {
    position: absolute;
    background: rgba(151,169,191,.10);
}

.ms-cross-h { left: 7%; right: 7%; top: 50%; height: 1px; }
.ms-cross-v { top: 7%; bottom: 7%; left: 50%; width: 1px; }

.ms-core {
    position: absolute;
    inset: 0;
    display: grid;
    place-items: center;
    z-index: 2;
    text-align: center;
}

.ms-core strong {
    display: block;
    color: var(--ivory);
    font-family: "Iowan Old Style", "Palatino Linotype", Georgia, serif;
    font-size: 2rem;
    font-weight: 500;
}

.ms-core span {
    color: var(--muted-2);
    font-size: .58rem;
    letter-spacing: .18em;
    text-transform: uppercase;
}

.ms-float-label {
    position: absolute;
    padding: .5rem .65rem;
    border: 1px solid rgba(151,169,191,.14);
    background: rgba(7,17,31,.84);
    color: #aab7c6;
    font-size: .58rem;
    letter-spacing: .13em;
    text-transform: uppercase;
    backdrop-filter: blur(9px);
}

.ms-float-label.one { right: -1.2rem; top: 18%; }
.ms-float-label.two { left: -1.5rem; bottom: 25%; }
.ms-float-label.three { right: -.2rem; bottom: 5%; }

/* Section headers */
.ms-section-head {
    margin: 2.0rem 0 .95rem;
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    gap: 1rem;
}

.ms-section-title {
    margin-top: .3rem;
    color: var(--ivory);
    font-family: "Iowan Old Style", "Palatino Linotype", Georgia, serif;
    font-size: 1.65rem;
    letter-spacing: -.025em;
}

.ms-section-copy {
    color: var(--muted-2);
    font-size: .72rem;
    line-height: 1.6;
    text-align: right;
    max-width: 460px;
}

/* Native Streamlit controls */
[data-testid="stFileUploader"],
[data-testid="stSelectbox"],
[data-testid="stTextInput"] {
    margin-bottom: .6rem;
}

[data-testid="stFileUploader"] > label,
[data-testid="stSelectbox"] > label {
    color: #a7b2c0 !important;
    font-size: .70rem !important;
    letter-spacing: .10em;
    text-transform: uppercase;
    font-weight: 620;
}

[data-testid="stFileUploaderDropzone"] {
    position: relative;
    min-height: 12.4rem;
    border: 1px solid rgba(215,194,154,.18) !important;
    border-radius: 7px !important;
    background:
        linear-gradient(rgba(13,25,40,.67), rgba(10,20,33,.72)) !important;
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    transition: border-color .25s ease, transform .25s ease, box-shadow .25s ease;
    overflow: hidden;
}

[data-testid="stFileUploaderDropzone"]::before {
    content: "RADIOGRAPH INPUT";
    position: absolute;
    left: 1rem;
    top: .9rem;
    color: rgba(215,194,154,.58);
    font-size: .56rem;
    letter-spacing: .18em;
}

[data-testid="stFileUploaderDropzone"]::after {
    content: "";
    position: absolute;
    left: -20%;
    right: -20%;
    top: 50%;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(65,105,168,.26), transparent);
    transform: translateY(-50%);
}

[data-testid="stFileUploaderDropzone"]:hover {
    border-color: rgba(215,194,154,.42) !important;
    box-shadow: 0 18px 55px rgba(0,0,0,.20), inset 0 0 80px rgba(65,105,168,.028);
    transform: translateY(-1px);
}

[data-testid="stFileUploaderDropzone"] button {
    background: rgba(245,241,232,.95) !important;
    color: #07111f !important;
    border: 1px solid rgba(215,194,154,.50) !important;
    border-radius: 4px !important;
    font-weight: 700 !important;
}

div[data-baseweb="select"] > div {
    min-height: 3.15rem;
    background: linear-gradient(145deg, rgba(16,29,48,.72), rgba(11,23,40,.76)) !important;
    backdrop-filter: blur(9px);
    -webkit-backdrop-filter: blur(9px);
    border: 1px solid rgba(151,169,191,.17) !important;
    border-radius: 5px !important;
    color: var(--ivory) !important;
    box-shadow: none !important;
}

ul[role="listbox"] {
    background: #0d1928 !important;
}

li[role="option"] {
    color: #e6e1d8 !important;
}

.stButton > button,
.stDownloadButton > button {
    width: 100%;
    min-height: 3.15rem;
    border-radius: 4px !important;
    border: 1px solid rgba(215,194,154,.42) !important;
    background: linear-gradient(100deg, #f3eee4 0%, #ded1b8 100%) !important;
    color: #07111f !important;
    font-weight: 760 !important;
    letter-spacing: .08em;
    text-transform: uppercase;
    font-size: .72rem !important;
    box-shadow: 0 12px 30px rgba(0,0,0,.18);
    transition: transform .22s ease, box-shadow .22s ease, filter .22s ease;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    transform: translateY(-2px);
    filter: brightness(1.035);
    box-shadow: 0 18px 44px rgba(0,0,0,.28);
}

.stButton > button:disabled {
    opacity: .44;
    transform: none;
}

/* Dark secondary download button when inside export area */
.ms-dark-action + div .stDownloadButton > button {
    background: rgba(255,255,255,.024) !important;
    color: var(--ivory-soft) !important;
    border-color: rgba(151,169,191,.18) !important;
}

/* Panels */
.ms-panel,
.ms-info-panel,
.ms-metric,
.ms-urgency,
.ms-report-shell,
.ms-summary-shell,
.ms-trace-shell {
    border: 1px solid rgba(151,169,191,.14);
    background: linear-gradient(145deg, rgba(16,29,48,.66), rgba(10,21,36,.72));
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    box-shadow: 0 14px 55px rgba(0,0,0,.15);
}

.ms-panel {
    padding: 1.3rem 1.35rem;
    min-height: 100%;
}

.ms-panel.gold-edge,
.ms-report-shell {
    border-top-color: rgba(215,194,154,.42);
}

.ms-panel-title {
    color: var(--ivory);
    font-size: .83rem;
    font-weight: 690;
    letter-spacing: .06em;
    text-transform: uppercase;
}

.ms-panel-copy {
    margin-top: .5rem;
    color: var(--muted);
    font-size: .76rem;
    line-height: 1.65;
}

.ms-workflow-list {
    margin-top: 1rem;
    display: grid;
    gap: .62rem;
}

.ms-workflow-row {
    display: grid;
    grid-template-columns: 2.25rem 1fr auto;
    align-items: center;
    gap: .75rem;
    padding: .67rem 0;
    border-bottom: 1px solid rgba(151,169,191,.09);
}

.ms-workflow-row:last-child { border-bottom: 0; }

.ms-workflow-no {
    color: var(--champagne);
    font-family: "Iowan Old Style", "Palatino Linotype", Georgia, serif;
    font-size: .92rem;
}

.ms-workflow-main {
    color: #cbd2dc;
    font-size: .70rem;
    letter-spacing: .055em;
    text-transform: uppercase;
}

.ms-workflow-state {
    color: var(--muted-2);
    font-size: .55rem;
    letter-spacing: .12em;
    text-transform: uppercase;
}

.ms-note {
    margin-top: .85rem;
    padding: .8rem .9rem;
    border-left: 2px solid rgba(183,154,91,.58);
    background: rgba(183,154,91,.045);
    color: #9ba7b6;
    font-size: .68rem;
    line-height: 1.62;
}

/* Image styling */
[data-testid="stImage"] {
    overflow: hidden;
    border: 1px solid rgba(151,169,191,.14);
    background: #04080d;
    box-shadow: 0 18px 55px rgba(0,0,0,.23);
}

[data-testid="stImage"] img {
    filter: saturate(.93) contrast(1.01);
}

[data-testid="stImageCaption"] {
    color: #7f8da0 !important;
    font-size: .62rem !important;
    letter-spacing: .11em;
    text-transform: uppercase;
}

/* Result metrics */
.ms-metrics {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: .8rem;
    margin: .9rem 0 1.4rem;
}

.ms-metric {
    position: relative;
    padding: 1rem 1.05rem;
    overflow: hidden;
}

.ms-metric::after {
    content: "";
    position: absolute;
    inset: auto 0 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(215,194,154,.22), transparent);
}

.ms-metric-label {
    color: var(--muted-2);
    font-size: .58rem;
    letter-spacing: .15em;
    text-transform: uppercase;
}

.ms-metric-value {
    margin-top: .35rem;
    color: var(--ivory);
    font-family: "Iowan Old Style", "Palatino Linotype", Georgia, serif;
    font-size: 1.65rem;
}

.ms-metric-sub {
    margin-top: .15rem;
    color: #758398;
    font-size: .62rem;
}

/* Findings */
.ms-findings-shell {
    padding: 1.25rem 1.35rem 1.1rem;
    border: 1px solid rgba(151,169,191,.14);
    background: linear-gradient(145deg, rgba(13,25,40,.64), rgba(8,18,31,.70));
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
}

.ms-finding-row {
    padding: .82rem 0 .88rem;
    border-bottom: 1px solid rgba(151,169,191,.08);
}

.ms-finding-row:last-child { border-bottom: 0; }

.ms-finding-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    margin-bottom: .53rem;
}

.ms-finding-name {
    color: #dce1e8;
    font-size: .76rem;
    font-weight: 620;
}

.ms-finding-score {
    color: var(--champagne);
    font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
    font-size: .68rem;
}

.ms-track {
    height: 4px;
    background: rgba(151,169,191,.09);
    overflow: hidden;
}

.ms-fill {
    height: 100%;
    transform-origin: left center;
    background: linear-gradient(90deg, #345c94, #708db7 68%, #b79a5b 100%);
    animation: medscribeBar 1s cubic-bezier(.2,.8,.2,1) both;
}

.ms-empty-findings {
    padding: 1rem 0 .25rem;
    color: #8795a8;
    font-size: .74rem;
    line-height: 1.65;
}

/* Urgency */
.ms-urgency {
    padding: 1.05rem 1.1rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
}

.ms-urgency-left {
    display: flex;
    align-items: center;
    gap: .8rem;
}

.ms-urgency-dot {
    width: .62rem;
    height: .62rem;
    border-radius: 50%;
}

.ms-urgency-dot.routine { background: var(--success); }
.ms-urgency-dot.urgent { background: var(--warning); }
.ms-urgency-dot.critical { background: var(--critical); }

.ms-urgency-name {
    color: var(--ivory);
    font-size: .78rem;
    font-weight: 700;
    letter-spacing: .11em;
    text-transform: uppercase;
}

.ms-urgency-caption {
    color: var(--muted-2);
    font-size: .62rem;
    margin-top: .16rem;
}

.ms-urgency-code {
    color: #7f8da0;
    font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
    font-size: .61rem;
}

.ms-critical-alert {
    margin-top: .72rem;
    border: 1px solid rgba(199,91,100,.30);
    border-left: 3px solid rgba(199,91,100,.80);
    background: rgba(199,91,100,.055);
    padding: .85rem .95rem;
    color: #cbb1b4;
    font-size: .70rem;
    line-height: 1.6;
}

/* Report / summary */
.ms-report-shell,
.ms-summary-shell,
.ms-trace-shell {
    padding: 1.25rem 1.35rem;
}

.ms-report-shell + div,
.ms-summary-shell + div {
    margin-top: -.25rem;
}

.ms-report-heading {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    padding-bottom: .75rem;
    margin-bottom: .35rem;
    border-bottom: 1px solid rgba(151,169,191,.09);
}

.ms-report-title {
    color: var(--ivory);
    font-family: "Iowan Old Style", "Palatino Linotype", Georgia, serif;
    font-size: 1.28rem;
}

.ms-report-meta {
    color: var(--muted-2);
    font-size: .57rem;
    letter-spacing: .14em;
    text-transform: uppercase;
}

.ms-summary-text {
    color: #c8d0da;
    font-size: .82rem;
    line-height: 1.86;
    white-space: pre-wrap;
}

.ms-summary-text[dir="rtl"] {
    font-family: "Noto Nastaliq Urdu", "Noto Naskh Arabic", "Segoe UI", sans-serif;
    font-size: 1rem;
    line-height: 2.05;
    text-align: right;
}

/* markdown report appearance */
.ms-report-marker + div [data-testid="stMarkdownContainer"] {
    color: #c9d1da;
    font-size: .83rem;
    line-height: 1.78;
}

.ms-report-marker + div [data-testid="stMarkdownContainer"] h1,
.ms-report-marker + div [data-testid="stMarkdownContainer"] h2,
.ms-report-marker + div [data-testid="stMarkdownContainer"] h3 {
    font-family: "Iowan Old Style", "Palatino Linotype", Georgia, serif;
    color: var(--ivory);
}

/* Trace */
.ms-trace-item {
    display: grid;
    grid-template-columns: 2.4rem 1fr;
    gap: .85rem;
    position: relative;
    padding: .15rem 0 1.05rem;
}

.ms-trace-item:not(:last-child)::after {
    content: "";
    position: absolute;
    left: 1.16rem;
    top: 2.15rem;
    bottom: .1rem;
    width: 1px;
    background: linear-gradient(to bottom, rgba(215,194,154,.30), rgba(151,169,191,.08));
}

.ms-trace-no {
    width: 2.35rem;
    height: 2.35rem;
    display: grid;
    place-items: center;
    border: 1px solid rgba(215,194,154,.22);
    color: var(--champagne);
    font-family: "Iowan Old Style", "Palatino Linotype", Georgia, serif;
    font-size: .78rem;
    background: rgba(183,154,91,.025);
}

.ms-trace-tool {
    color: #d7dde5;
    font-size: .72rem;
    font-weight: 690;
    letter-spacing: .06em;
    text-transform: uppercase;
}

.ms-trace-desc {
    margin-top: .2rem;
    color: #7f8da0;
    font-size: .65rem;
    line-height: 1.55;
}

.ms-trace-args {
    margin-top: .38rem;
    color: #8492a4;
    font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
    font-size: .57rem;
    line-height: 1.52;
    word-break: break-word;
}

/* Tabs */
[data-baseweb="tab-list"] {
    gap: .35rem !important;
    border-bottom: 1px solid rgba(151,169,191,.10);
}

button[data-baseweb="tab"] {
    min-height: 2.8rem;
    padding: 0 1rem !important;
    border-radius: 0 !important;
    color: #7f8da0 !important;
    font-size: .66rem !important;
    font-weight: 680 !important;
    letter-spacing: .10em !important;
    text-transform: uppercase;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: var(--ivory) !important;
}

[data-baseweb="tab-highlight"] {
    background: var(--champagne) !important;
    height: 1px !important;
}

/* Streamlit alerts and spinner */
[data-testid="stAlert"] {
    border-radius: 4px !important;
    border: 1px solid rgba(151,169,191,.16) !important;
    background: rgba(13,25,40,.70) !important;
    backdrop-filter: blur(9px);
    -webkit-backdrop-filter: blur(9px);
    color: #cbd3dd !important;
}

[data-testid="stSpinner"] > div {
    color: var(--champagne) !important;
}

/* Progress */
[data-testid="stProgress"] > div > div > div > div {
    background: linear-gradient(90deg, var(--sapphire), var(--champagne)) !important;
}

/* Divider */
hr {
    border-color: rgba(151,169,191,.10) !important;
}

/* Footer */
.ms-footer {
    margin-top: 2.7rem;
    padding-top: 1.15rem;
    border-top: 1px solid rgba(215,194,154,.11);
    display: flex;
    justify-content: space-between;
    gap: 1.3rem;
    color: #627186;
    font-size: .60rem;
    line-height: 1.65;
    letter-spacing: .035em;
}

.ms-footer strong {
    color: #8794a6;
    font-weight: 650;
}

/* Responsive */
@media (max-width: 900px) {
    .block-container { padding-left: 1rem; padding-right: 1rem; }
    .ms-hero {
        grid-template-columns: 1fr;
        padding: 2.4rem 1.5rem;
    }
    .ms-hero h1 { font-size: clamp(3rem, 15vw, 5rem); }
    .ms-visual { min-height: 15rem; }
    .ms-orbit { width: 14rem; }
    .ms-float-label.one { right: .2rem; }
    .ms-float-label.two { left: .2rem; }
    .ms-section-head { align-items: flex-start; flex-direction: column; }
    .ms-section-copy { text-align: left; }
    .ms-metrics { grid-template-columns: 1fr; }
    .ms-footer { flex-direction: column; }
}

@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation-duration: .001ms !important;
        animation-iteration-count: 1 !important;
        scroll-behavior: auto !important;
    }
}





/* Primary clinical action — royal gold */
.stButton > button[kind="primary"],
button[data-testid="stBaseButton-primary"] {
    background: linear-gradient(
        100deg,
        #A98642 0%,
        #B79A5B 42%,
        #D7C29A 100%
    ) !important;
    color: #07111F !important;
    border: 1px solid rgba(231, 208, 158, .78) !important;
    box-shadow:
        0 12px 30px rgba(183,154,91,.18),
        inset 0 1px 0 rgba(255,255,255,.16) !important;
}

.stButton > button[kind="primary"]:hover,
button[data-testid="stBaseButton-primary"]:hover {
    background: linear-gradient(
        100deg,
        #B18E49 0%,
        #C1A464 45%,
        #DEC99F 100%
    ) !important;
    color: #07111F !important;
    filter: none !important;
    box-shadow:
        0 16px 38px rgba(183,154,91,.28),
        inset 0 1px 0 rgba(255,255,255,.20) !important;
}

/* Keep the gold identity visible before an image is uploaded */
.stButton > button[kind="primary"]:disabled,
button[data-testid="stBaseButton-primary"]:disabled {
    background: linear-gradient(
        100deg,
        rgba(169,134,66,.88) 0%,
        rgba(183,154,91,.88) 42%,
        rgba(215,194,154,.88) 100%
    ) !important;
    color: rgba(7,17,31,.82) !important;
    opacity: .72 !important;
    border-color: rgba(215,194,154,.58) !important;
    box-shadow: 0 8px 22px rgba(183,154,91,.10) !important;
}



/* Run Clinical Analysis — force high-contrast text on gold */
.stButton > button[kind="primary"],
button[data-testid="stBaseButton-primary"] {
    color: #07111F !important;
    font-weight: 800 !important;
}

.stButton > button[kind="primary"] *,
button[data-testid="stBaseButton-primary"] * {
    color: #07111F !important;
    fill: #07111F !important;
    opacity: 1 !important;
    font-weight: 800 !important;
    text-shadow: none !important;
}

/* Disabled state: still readable, just slightly muted */
.stButton > button[kind="primary"]:disabled,
button[data-testid="stBaseButton-primary"]:disabled {
    color: rgba(7,17,31,.82) !important;
}

.stButton > button[kind="primary"]:disabled *,
button[data-testid="stBaseButton-primary"]:disabled * {
    color: rgba(7,17,31,.82) !important;
    fill: rgba(7,17,31,.82) !important;
    opacity: 1 !important;
}

</style>
"""

st.markdown(ROYAL_CSS, unsafe_allow_html=True)
st.markdown('<div class="royal-grid"></div>', unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def esc(value: Any) -> str:
    return html.escape("" if value is None else str(value))


def normalize_urgency(value: Any) -> str:
    raw = str(value or "routine").strip().lower().replace('"', "").replace("'", "")
    if "critical" in raw:
        return "critical"
    if "urgent" in raw:
        return "urgent"
    return "routine"


def safe_suffix(filename: str) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix not in {".png", ".jpg", ".jpeg"}:
        return ".png"
    return suffix


def top_confidence(findings: list[dict[str, Any]]) -> float:
    if not findings:
        return 0.0
    return max(float(item.get("confidence", 0) or 0) for item in findings)


def trace_description(tool_name: str) -> str:
    descriptions = {
        "detect_findings": "Vision inference · DenseNet121 pathology screening",
        "write_clinical_report": "Clinical synthesis · structured radiology report",
        "assess_urgency": "Triage layer · routine / urgent / critical classification",
        "write_patient_summary": "Communication layer · patient-friendly language output",
        "escalate_to_doctor": "Escalation layer · on-call radiologist alert",
    }
    return descriptions.get(tool_name, "Agent tool execution")


def compact_args(args: Any, limit: int = 220) -> str:
    try:
        text = json.dumps(args, ensure_ascii=False, default=str)
    except Exception:
        text = str(args)
    text = " ".join(text.split())
    return text if len(text) <= limit else text[: limit - 1] + "…"



def render_golden_dust_background() -> None:
    """
    Inject a full-viewport golden shimmer plume behind the Streamlit UI.

    The effect is inspired by floating glitter / energy-smoke particles:
    a concentrated sinuous gold stream runs from top to bottom, surrounded
    by sparse drifting dust. Nearby particles move away from the cursor and
    spring back toward the plume.
    """
    components.html(
        """
        <script>
        (function () {
          let parentWin;
          let parentDoc;

          try {
            parentWin = window.parent;
            parentDoc = parentWin.document;
          } catch (err) {
            return;
          }

          if (!parentDoc || !parentDoc.body) return;

          const oldRoot =
            parentDoc.getElementById("ms-gold-plume-root") ||
            parentDoc.getElementById("ms-dna-gold-root") ||
            parentDoc.getElementById("ms-golden-dust-root");
          if (oldRoot) oldRoot.remove();

          const oldStyle =
            parentDoc.getElementById("ms-gold-plume-style") ||
            parentDoc.getElementById("ms-dna-gold-style") ||
            parentDoc.getElementById("ms-golden-dust-style");
          if (oldStyle) oldStyle.remove();

          const style = parentDoc.createElement("style");
          style.id = "ms-gold-plume-style";
          style.textContent = `
            #ms-gold-plume-root {
              position: fixed;
              inset: 0;
              z-index: 1;
              pointer-events: none;
              overflow: hidden;
            }

            #ms-gold-plume-canvas {
              position: absolute;
              inset: 0;
              width: 100%;
              height: 100%;
              display: block;
              pointer-events: none;
              opacity: 1;
              filter: none;
            }

            @media (prefers-reduced-motion: reduce) {
              #ms-gold-plume-canvas { opacity: .42; }
            }
          `;
          parentDoc.head.appendChild(style);

          const root = parentDoc.createElement("div");
          root.id = "ms-gold-plume-root";

          const canvas = parentDoc.createElement("canvas");
          canvas.id = "ms-gold-plume-canvas";
          root.appendChild(canvas);
          parentDoc.body.appendChild(root);

          const ctx = canvas.getContext("2d", { alpha: true });
          if (!ctx) return;

          let width = 1;
          let height = 1;
          let dpr = 1;

          let targetMouseX = -10000;
          let targetMouseY = -10000;
          let mouseX = -10000;
          let mouseY = -10000;

          let scrollY = parentWin.scrollY || 0;
          let smoothScrollY = scrollY;

          const plumeParticles = [];
          const ambientParticles = [];
          const totalPlume = 820;
          const totalAmbient = 265;

          function rand(seed) {
            const x = Math.sin(seed * 12.9898 + 78.233) * 43758.5453;
            return x - Math.floor(x);
          }

          function resetParticles() {
            plumeParticles.length = 0;
            ambientParticles.length = 0;

            for (let i = 0; i < totalPlume; i++) {
              const t = rand(i * 2.17 + 5.1);

              // Most particles live close to the bright core,
              // with a smaller number forming the outer smoke halo.
              const coreBias = Math.pow(rand(i * 3.91 + 8.2), 2.15);
              const side = rand(i * 7.33 + 4.6) > .5 ? 1 : -1;

              plumeParticles.push({
                t,
                side,
                radial: 7 + coreBias * 118,
                verticalJitter: (rand(i * 5.27 + 1.8) - .5) * 28,
                phase: rand(i * 9.1 + 3.2) * Math.PI * 2,
                size: .34 + rand(i * 4.51 + 7.4) * 1.72,
                alpha: .075 + rand(i * 8.77 + 2.1) * .48,
                warmth: rand(i * 6.12 + 6.4),
                ox: 0,
                oy: 0,
                vx: 0,
                vy: 0
              });
            }

            for (let i = 0; i < totalAmbient; i++) {
              ambientParticles.push({
                x: rand(i * 3.7 + 1.1),
                y: rand(i * 5.4 + 2.8),
                phase: rand(i * 7.9 + 9.4) * Math.PI * 2,
                size: .24 + rand(i * 9.2 + 4.3) * 1.16,
                alpha: .040 + rand(i * 6.7 + 7.5) * .20,
                driftX: (rand(i * 4.9 + 3.6) - .5) * 16,
                driftY: 8 + rand(i * 2.8 + 5.9) * 26,
                ox: 0,
                oy: 0,
                vx: 0,
                vy: 0
              });
            }
          }

          function resize() {
            width = Math.max(
              1,
              parentWin.innerWidth || parentDoc.documentElement.clientWidth || 1
            );
            height = Math.max(
              1,
              parentWin.innerHeight || parentDoc.documentElement.clientHeight || 1
            );

            dpr = Math.min(2, parentWin.devicePixelRatio || 1);
            canvas.width = Math.floor(width * dpr);
            canvas.height = Math.floor(height * dpr);
            canvas.style.width = width + "px";
            canvas.style.height = height + "px";
            ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
          }

          resetParticles();
          resize();

          function onMouseMove(e) {
            targetMouseX = e.clientX;
            targetMouseY = e.clientY;
          }

          function onMouseLeave() {
            targetMouseX = -10000;
            targetMouseY = -10000;
          }

          function onScroll() {
            scrollY =
              parentWin.scrollY ||
              parentDoc.documentElement.scrollTop ||
              0;
          }

          parentWin.addEventListener("mousemove", onMouseMove, { passive: true });
          parentWin.addEventListener("mouseleave", onMouseLeave, { passive: true });
          parentWin.addEventListener("scroll", onScroll, { passive: true });
          parentWin.addEventListener("resize", resize, { passive: true });

          function plumeCenter(t, time) {
            // A graceful S-shaped vertical plume, rather than a literal DNA helix.
            const scrollPhase = smoothScrollY * .00055;

            const centerX =
              width * .53 +
              Math.sin(t * Math.PI * 2.25 + time * .00011 + scrollPhase) *
                Math.min(width * .095, 120) +
              Math.sin(t * Math.PI * 5.1 - time * .00007) *
                Math.min(width * .028, 38);

            const y =
              -height * .10 +
              t * height * 1.20 +
              Math.sin(t * Math.PI * 3.8 + time * .00016) * 10;

            return { x: centerX, y };
          }

          function plumeTangent(t, time) {
            const eps = .002;
            const a = plumeCenter(Math.max(0, t - eps), time);
            const b = plumeCenter(Math.min(1, t + eps), time);

            let tx = b.x - a.x;
            let ty = b.y - a.y;
            const len = Math.sqrt(tx * tx + ty * ty) || 1;

            tx /= len;
            ty /= len;

            return {
              tx,
              ty,
              nx: -ty,
              ny: tx
            };
          }

          function repel(p, homeX, homeY, radius, strength) {
            const px = homeX + p.ox;
            const py = homeY + p.oy;

            const dx = px - mouseX;
            const dy = py - mouseY;
            const d2 = dx * dx + dy * dy;
            const r2 = radius * radius;

            if (d2 < r2 && d2 > .001) {
              const d = Math.sqrt(d2);
              const f = (1 - d / radius) * strength;
              p.vx += (dx / d) * f;
              p.vy += (dy / d) * f;
            }

            // Elastic return to the original plume.
            p.vx += (-p.ox) * .017;
            p.vy += (-p.oy) * .017;
            p.vx *= .90;
            p.vy *= .90;
            p.ox += p.vx;
            p.oy += p.vy;
          }

          function glow(x, y, radius, alpha) {
            const g = ctx.createRadialGradient(x, y, 0, x, y, radius);
            g.addColorStop(0, `rgba(215,194,154,${alpha})`);
            g.addColorStop(.30, `rgba(183,154,91,${alpha * .62})`);
            g.addColorStop(.72, `rgba(183,154,91,${alpha * .16})`);
            g.addColorStop(1, "rgba(183,154,91,0)");

            ctx.fillStyle = g;
            ctx.beginPath();
            ctx.arc(x, y, radius, 0, Math.PI * 2);
            ctx.fill();
          }

          function drawPlumeParticle(p, time) {
            const center = plumeCenter(p.t, time);
            const tangent = plumeTangent(p.t, time);

            const wave =
              Math.sin(time * .00065 + p.phase + p.t * 18) * 8;

            const homeX =
              center.x +
              tangent.nx * (p.radial * p.side + wave);

            const homeY =
              center.y +
              tangent.ny * (p.radial * p.side + wave * .35) +
              p.verticalJitter +
              Math.cos(time * .00042 + p.phase) * 6;

            repel(p, homeX, homeY, 135, 2.45);

            const x = homeX + p.ox;
            const y = homeY + p.oy;

            const shimmer =
              .18 +
              .82 * (
                .5 +
                .5 * Math.sin(
                  time * .0031 +
                  p.phase +
                  p.t * 31
                )
              );

            const alpha =
              Math.min(
                .82,
                p.alpha *
                (.34 + shimmer * 1.72) *
                (1 - Math.min(1, p.radial / 160) * .28)
              );

            const size = p.size * (.96 + shimmer * .08);

            const colorMix = p.warmth;
            const r = Math.round(183 + (215 - 183) * colorMix);
            const g = Math.round(154 + (194 - 154) * colorMix);
            const b = Math.round(91 + (154 - 91) * colorMix);

            ctx.fillStyle = `rgba(${r},${g},${b},${alpha})`;
            ctx.beginPath();
            ctx.arc(x, y, Math.max(.28, size), 0, Math.PI * 2);
            ctx.fill();

          }

          function drawAmbient(p, time) {
            const baseX =
              p.x * width +
              Math.sin(time * .00022 + p.phase) * p.driftX;

            const baseY =
              ((p.y * height +
                time * .006 * p.driftY -
                smoothScrollY * .07) %
                (height + 70)) -
              35;

            repel(p, baseX, baseY, 105, 1.6);

            const x = baseX + p.ox;
            const y = baseY + p.oy;

            const shimmer =
              .20 +
              .80 * (
                .5 +
                .5 * Math.sin(time * .0020 + p.phase)
              );

            const alpha = Math.min(.42, p.alpha * (.30 + shimmer * 1.55));
            const size = p.size * (.97 + shimmer * .06);

            ctx.fillStyle = `rgba(183,154,91,${alpha})`;
            ctx.beginPath();
            ctx.arc(x, y, size, 0, Math.PI * 2);
            ctx.fill();
          }

          function drawSoftSmoke(time) {
            // Very soft golden illumination along the same path.
            ctx.save();
            ctx.globalCompositeOperation = "screen";

            for (let i = 0; i < 22; i++) {
              const t = i / 21;
              const c = plumeCenter(t, time);
              const pulse =
                .78 +
                .22 * Math.sin(time * .0007 + i * .77);

              const radius =
                52 +
                Math.sin(t * Math.PI) * 42 +
                pulse * 15;

              const grad = ctx.createRadialGradient(
                c.x, c.y, 0,
                c.x, c.y, radius
              );

              grad.addColorStop(
                0,
                `rgba(183,154,91,${.014 + pulse * .012})`
              );
              grad.addColorStop(
                .40,
                `rgba(183,154,91,${.008 + pulse * .008})`
              );
              grad.addColorStop(1, "rgba(203,138,26,0)");

              ctx.fillStyle = grad;
              ctx.beginPath();
              ctx.arc(c.x, c.y, radius, 0, Math.PI * 2);
              ctx.fill();
            }

            ctx.restore();
          }

          function render(time) {
            mouseX += (targetMouseX - mouseX) * .17;
            mouseY += (targetMouseY - mouseY) * .17;
            smoothScrollY += (scrollY - smoothScrollY) * .08;

            ctx.clearRect(0, 0, width, height);

            drawSoftSmoke(time);

            // Ambient dust first.
            for (const p of ambientParticles) {
              drawAmbient(p, time);
            }

            // Main concentrated glitter plume.
            for (const p of plumeParticles) {
              drawPlumeParticle(p, time);
            }

            parentWin.requestAnimationFrame(render);
          }

          parentWin.requestAnimationFrame(render);
        })();
        </script>
        """,
        height=0,
        scrolling=False,
    )


def render_topbar() -> None:
    st.markdown(
        """
        <div class="ms-topbar">
            <div class="ms-brand">
                <div class="ms-monogram">MS</div>
                <div>
                    <div class="ms-brand-name">MedScribe AI</div>
                    <div class="ms-brand-meta">Radiology Intelligence</div>
                </div>
            </div>
            <div class="ms-system">
                <span class="ms-system-dot"></span>
                System operational
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_hero() -> None:
    """Render the luxury hero with a real interactive 3D adult-male chest model.

    The model is embedded from Sketchfab (CC BY) and remains confined to the
    right-hand hero viewer. It auto-rotates slowly and supports mouse/touch drag.
    """
    hero_html = r"""
    <!doctype html>
    <html lang="en">
    <head>
      <meta charset="utf-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1" />
      <style>
        :root {
          --bg: #07111f;
          --surface: #0b1728;
          --surface-2: #101d30;
          --ivory: #f5f1e8;
          --muted: #91a0b2;
          --muted-2: #657488;
          --gold: #b79a5b;
          --champagne: #d7c29a;
          --success: #58a889;
          --line: rgba(151,169,191,.14);
        }

        * { box-sizing: border-box; }
        html, body {
          margin: 0;
          width: 100%;
          height: 100%;
          overflow: hidden;
          background: transparent;
          color: var(--ivory);
          font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        }

        .hero {
          position: relative;
          height: 410px;
          display: grid;
          grid-template-columns: minmax(0, 1.08fr) minmax(420px, .92fr);
          gap: 26px;
          align-items: center;
          padding: 34px 36px;
          overflow: hidden;
          border: 1px solid rgba(215,194,154,.15);
          background:
            radial-gradient(circle at 84% 48%, rgba(65,105,168,.10), transparent 31%),
            linear-gradient(110deg, rgba(13,25,40,.84), rgba(8,18,31,.78));
          box-shadow: 0 24px 70px rgba(0,0,0,.25);
        }

        .hero::before {
          content: "";
          position: absolute;
          inset: 0;
          pointer-events: none;
          background-image:
            linear-gradient(rgba(140,157,180,.025) 1px, transparent 1px),
            linear-gradient(90deg, rgba(140,157,180,.025) 1px, transparent 1px);
          background-size: 62px 62px;
          mask-image: linear-gradient(to right, rgba(0,0,0,.68), rgba(0,0,0,.12));
        }

        .hero::after {
          content: "";
          position: absolute;
          left: 0;
          top: 0;
          width: 100%;
          height: 1px;
          background: linear-gradient(90deg, transparent, rgba(215,194,154,.55), transparent);
        }

        .copy {
          position: relative;
          z-index: 3;
          padding-left: 3px;
        }

        .eyebrow {
          color: var(--champagne);
          font-size: 10px;
          font-weight: 700;
          letter-spacing: .19em;
          text-transform: uppercase;
        }

        h1 {
          margin: 14px 0 14px;
          max-width: 760px;
          color: var(--ivory);
          font-family: "Iowan Old Style", "Palatino Linotype", Georgia, serif;
          font-size: clamp(46px, 5vw, 68px);
          line-height: .94;
          font-weight: 500;
          letter-spacing: -.052em;
        }

        h1 span { color: var(--champagne); }

        .copy p {
          margin: 0;
          max-width: 650px;
          color: #96a5b6;
          font-size: 14px;
          line-height: 1.72;
        }

        .caps {
          display: grid;
          grid-template-columns: repeat(3, minmax(0, 1fr));
          gap: 9px;
          margin-top: 25px;
          max-width: 650px;
        }

        .cap {
          min-height: 69px;
          padding: 11px 12px 10px;
          border-top: 1px solid rgba(215,194,154,.26);
          background: rgba(255,255,255,.008);
        }

        .cap .no {
          display: block;
          color: var(--gold);
          font-family: Georgia, serif;
          font-size: 12px;
        }

        .cap b {
          display: block;
          margin-top: 4px;
          color: #d8dee6;
          font-size: 10px;
          letter-spacing: .13em;
          text-transform: uppercase;
        }

        .cap small {
          display: block;
          margin-top: 4px;
          color: #68798d;
          font-size: 8px;
          letter-spacing: .12em;
          text-transform: uppercase;
        }

        .viewer {
          position: relative;
          z-index: 3;
          height: 340px;
          overflow: hidden;
          border: 1px solid rgba(151,169,191,.12);
          background:
            radial-gradient(circle at 50% 46%, rgba(72,112,157,.14), transparent 44%),
            linear-gradient(180deg, rgba(4,13,23,.85), rgba(3,10,17,.65));
          box-shadow: inset 0 0 50px rgba(61,96,137,.05);
        }

        .viewer::before,
        .viewer::after {
          content: "";
          position: absolute;
          z-index: 4;
          pointer-events: none;
          border-radius: 50%;
          left: 50%;
          top: 50%;
          transform: translate(-50%, -50%);
        }

        .viewer::before {
          width: 250px;
          height: 250px;
          border: 1px solid rgba(163,185,209,.08);
          box-shadow: 0 0 42px rgba(75,115,159,.05);
          animation: ringSpin 22s linear infinite;
        }

        .viewer::after {
          width: 190px;
          height: 190px;
          border: 1px dashed rgba(215,194,154,.10);
          animation: ringSpinReverse 18s linear infinite;
        }

        .viewer-top {
          position: absolute;
          z-index: 7;
          left: 15px;
          right: 15px;
          top: 12px;
          display: flex;
          justify-content: space-between;
          align-items: center;
          pointer-events: none;
        }

        .viewer-label {
          color: #7b8c9f;
          font-size: 8px;
          letter-spacing: .17em;
          text-transform: uppercase;
        }

        .viewer-label b { color: #b8c4d0; font-weight: 700; }

        .live {
          display: flex;
          align-items: center;
          gap: 6px;
          color: #7b8c9f;
          font-size: 7px;
          letter-spacing: .16em;
          text-transform: uppercase;
        }

        .live i {
          width: 6px;
          height: 6px;
          border-radius: 50%;
          background: var(--success);
          box-shadow: 0 0 0 5px rgba(88,168,137,.07);
        }

        .model-frame {
          position: absolute;
          inset: 0;
          z-index: 2;
          width: 100%;
          height: 100%;
          border: 0;
          background: transparent;
          filter: saturate(.72) contrast(1.08) brightness(.95) hue-rotate(182deg);
        }

        .model-vignette {
          position: absolute;
          inset: 0;
          z-index: 5;
          pointer-events: none;
          background:
            linear-gradient(to bottom, rgba(4,13,23,.22), transparent 18%, transparent 80%, rgba(4,13,23,.34)),
            linear-gradient(90deg, rgba(4,13,23,.18), transparent 15%, transparent 85%, rgba(4,13,23,.18));
        }

        .scan {
          position: absolute;
          z-index: 6;
          left: 13%;
          right: 13%;
          top: 50%;
          height: 1px;
          pointer-events: none;
          background: linear-gradient(90deg, transparent, rgba(169,215,255,.38), transparent);
          box-shadow: 0 0 15px rgba(86,150,206,.14);
          animation: scan 6.8s ease-in-out infinite alternate;
        }

        .node {
          position: absolute;
          z-index: 6;
          width: 6px;
          height: 6px;
          border-radius: 50%;
          background: #eff6ff;
          box-shadow: 0 0 14px rgba(215,234,255,.34);
          pointer-events: none;
        }

        .n1 { right: 84px; top: 76px; animation: nodeA 5.5s ease-in-out infinite; }
        .n2 { left: 70px; bottom: 77px; animation: nodeB 6.4s ease-in-out infinite; }

        .viewer-bottom {
          position: absolute;
          z-index: 7;
          left: 15px;
          right: 15px;
          bottom: 9px;
          display: flex;
          justify-content: space-between;
          gap: 14px;
          pointer-events: none;
          color: #607186;
          font-size: 7px;
          letter-spacing: .12em;
          text-transform: uppercase;
        }

        .viewer-bottom b { color: #96a8ba; font-weight: 650; }

        .credit {
          position: absolute;
          z-index: 8;
          right: 13px;
          bottom: 27px;
          color: rgba(147,164,183,.62);
          font-size: 7px;
          letter-spacing: .05em;
          pointer-events: none;
        }

        @keyframes ringSpin {
          from { transform: translate(-50%, -50%) rotate(0deg); }
          to { transform: translate(-50%, -50%) rotate(360deg); }
        }
        @keyframes ringSpinReverse {
          from { transform: translate(-50%, -50%) rotate(360deg); }
          to { transform: translate(-50%, -50%) rotate(0deg); }
        }
        @keyframes scan {
          from { transform: translateY(-86px); }
          to { transform: translateY(86px); }
        }
        @keyframes nodeA {
          0%, 100% { transform: translate(0,0); }
          50% { transform: translate(-12px,10px); }
        }
        @keyframes nodeB {
          0%, 100% { transform: translate(0,0); }
          50% { transform: translate(12px,-8px); }
        }

        @media (max-width: 960px) {
          .hero {
            height: 680px;
            grid-template-columns: 1fr;
            padding: 28px 22px;
            gap: 22px;
          }
          h1 { font-size: 50px; }
          .viewer { height: 310px; }
        }

        @media (max-width: 620px) {
          .hero { height: 745px; padding: 24px 16px; }
          h1 { font-size: 41px; }
          .copy p { font-size: 12px; }
          .caps { grid-template-columns: 1fr; gap: 4px; margin-top: 16px; }
          .cap { min-height: 52px; padding: 8px 10px; }
          .viewer { height: 280px; }
        }

        @media (prefers-reduced-motion: reduce) {
          .viewer::before, .viewer::after, .scan, .node { animation: none !important; }
        }
      </style>
    </head>
    <body>
      <section class="hero">
        <div class="copy">
          <div class="eyebrow">Clinical intelligence / multimodal analysis</div>
          <h1>Precision at the point of <span>interpretation.</span></h1>
          <p>
            An agentic chest-radiograph workspace combining pathology detection,
            explainability, structured reporting, urgency triage and multilingual
            patient communication in one controlled workflow.
          </p>
          <div class="caps">
            <div class="cap"><span class="no">01</span><b>Vision</b><small>18 pathologies</small></div>
            <div class="cap"><span class="no">02</span><b>Explainability</b><small>Grad-CAM</small></div>
            <div class="cap"><span class="no">03</span><b>Synthesis</b><small>Clinical agent</small></div>
          </div>
        </div>

        <div class="viewer">
          <div class="viewer-top">
            <div class="viewer-label"><b>Interactive 3D chest</b></div>
          </div>

          <iframe
            class="model-frame"
            title="Adult male human thorax 3D model"
            frameborder="0"
            allow="autoplay; fullscreen; xr-spatial-tracking"
            allowfullscreen
            mozallowfullscreen="true"
            webkitallowfullscreen="true"
            src="https://sketchfab.com/models/4aba9b2ced344bdf8f09656c6a298b50/embed?autostart=1&autospin=0.18&ui_theme=dark&ui_infos=0&ui_help=0&ui_settings=0&ui_inspector=0&ui_stop=0&ui_hint=0&dnt=1">
          </iframe>

          <div class="model-vignette"></div>
          <div class="scan"></div>
          <div class="node n1"></div>
          <div class="node n2"></div>
        </div>
      </section>
    </body>
    </html>
    """
    components.html(hero_html, height=430, scrolling=False)


def section_header(index: str, title: str, copy: str) -> None:
    st.markdown(
        f"""
        <div class="ms-section-head">
            <div>
                <div class="ms-section-index">{esc(index)}</div>
                <div class="ms-section-title">{esc(title)}</div>
            </div>
            <div class="ms-section-copy">{esc(copy)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_workflow_panel() -> None:
    rows = [
        ("01", "Image ingestion", "Local input"),
        ("02", "Vision inference", "DenseNet121"),
        ("03", "Attention mapping", "Grad-CAM"),
        ("04", "Clinical synthesis", "Agent / LLM"),
        ("05", "Urgency + summary", "Final output"),
    ]
    rows_html = "".join(
        f"""
        <div class="ms-workflow-row">
            <div class="ms-workflow-no">{n}</div>
            <div class="ms-workflow-main">{name}</div>
            <div class="ms-workflow-state">{state}</div>
        </div>
        """
        for n, name, state in rows
    )
    st.markdown(
        f"""
        <div class="ms-panel gold-edge">
            <div class="ms-mini-label">Analysis architecture</div>
            <div class="ms-panel-title" style="margin-top:.45rem;">Controlled clinical workflow</div>
            <div class="ms-panel-copy">
                Each scan moves through the MedScribe clinical intelligence pipeline from image
                ingestion through explainability, synthesis, urgency assessment and patient communication.
            </div>
            <div class="ms-workflow-list">{rows_html}</div>
            <div class="ms-note">
                AI-assisted output requires qualified clinical review and must not be used as a standalone diagnosis.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_findings(findings: list[dict[str, Any]]) -> None:
    """Render model findings and confidence bars."""
    if not findings:
        rows_html = (
            '<div class="ms-empty-findings">'
            'No pathology exceeded the current model display threshold for this scan. '
            'This does not establish a normal study; clinical review remains required.'
            '</div>'
        )
    else:
        sorted_findings = sorted(
            findings,
            key=lambda item: float(item.get("confidence", 0) or 0),
            reverse=True,
        )

        row_parts: list[str] = []
        for item in sorted_findings:
            label = esc(item.get("label", "Finding"))
            confidence = max(
                0.0,
                min(1.0, float(item.get("confidence", 0) or 0)),
            )
            pct = confidence * 100

            row_parts.append(
                '<div class="ms-finding-row">'
                '<div class="ms-finding-head">'
                f'<div class="ms-finding-name">{label}</div>'
                f'<div class="ms-finding-score">{pct:.1f}%</div>'
                '</div>'
                '<div class="ms-track">'
                f'<div class="ms-fill" style="width:{pct:.1f}%"></div>'
                '</div>'
                '</div>'
            )

        rows_html = "".join(row_parts)

    findings_html = (
        '<div class="ms-findings-shell">'
        '<div class="ms-mini-label">Model observations</div>'
        '<div class="ms-panel-title" style="margin-top:.45rem;">Detected findings</div>'
        f'{rows_html}'
        '</div>'
    )

    st.markdown(findings_html, unsafe_allow_html=True)


def render_urgency(urgency: str, escalated: bool) -> None:
    captions = {
        "routine": "No critical escalation was returned by the agent.",
        "urgent": "Prioritized clinical review is recommended by the agent output.",
        "critical": "Critical classification returned by the agent workflow.",
    }
    st.markdown(
        f"""
        <div class="ms-urgency">
            <div class="ms-urgency-left">
                <span class="ms-urgency-dot {esc(urgency)}"></span>
                <div>
                    <div class="ms-urgency-name">{esc(urgency)}</div>
                    <div class="ms-urgency-caption">{esc(captions.get(urgency, captions['routine']))}</div>
                </div>
            </div>
            <div class="ms-urgency-code">TRIAGE / {esc(urgency.upper())}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if escalated:
        st.markdown(
            """
            <div class="ms-critical-alert">
                The analysis was flagged for escalation and requires prioritized clinical review.
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_trace(trace: list[dict[str, Any]]) -> None:
    if not trace:
        st.markdown(
            '<div class="ms-empty-findings">No agent tool trace was returned for this run.</div>',
            unsafe_allow_html=True,
        )
        return

    items = []
    for idx, step in enumerate(trace, start=1):
        tool_name = str(step.get("tool", "agent_step"))
        args = compact_args(step.get("args", {}))
        items.append(
            f"""
            <div class="ms-trace-item">
                <div class="ms-trace-no">{idx:02d}</div>
                <div>
                    <div class="ms-trace-tool">{esc(tool_name.replace('_', ' '))}</div>
                    <div class="ms-trace-desc">{esc(trace_description(tool_name))}</div>
                    <div class="ms-trace-args">{esc(args)}</div>
                </div>
            </div>
            """
        )

    st.markdown(
        '<div class="ms-trace-shell">' + "".join(items) + "</div>",
        unsafe_allow_html=True,
    )


def export_text(
    scan_name: str,
    language: str,
    findings: list[dict[str, Any]],
    result: dict[str, Any],
) -> str:
    finding_lines = []
    for item in sorted(
        findings,
        key=lambda x: float(x.get("confidence", 0) or 0),
        reverse=True,
    ):
        finding_lines.append(
            f"- {item.get('label', 'Finding')}: {float(item.get('confidence', 0) or 0) * 100:.1f}%"
        )
    if not finding_lines:
        finding_lines = ["- No displayed finding exceeded the model threshold."]

    urgency = normalize_urgency(result.get("urgency"))
    return f"""MEDSCRIBE AI — RADIOLOGY INTELLIGENCE
AI-assisted radiology analysis

SCAN
File: {scan_name}
Patient output language: {language}

MODEL FINDINGS
{chr(10).join(finding_lines)}

CLINICAL REPORT
{result.get('clinical_report') or 'No report returned.'}

URGENCY
{urgency.upper()}

PATIENT SUMMARY
{result.get('patient_summary') or 'No patient summary returned.'}

DISCLAIMER
This AI-assisted output requires qualified clinical review and is not a standalone diagnosis.
"""


# -----------------------------------------------------------------------------
# Session state
# -----------------------------------------------------------------------------
STATE_DEFAULTS = {
    "analysis_result": None,
    "analysis_findings": [],
    "analysis_heatmap": None,
    "analysis_scan_path": None,
    "analysis_scan_name": None,
    "analysis_language": None,
}
for key, value in STATE_DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


# -----------------------------------------------------------------------------
# Header / hero
# -----------------------------------------------------------------------------
render_golden_dust_background()
render_topbar()
render_hero()

# -----------------------------------------------------------------------------
# Input workspace
# -----------------------------------------------------------------------------
section_header(
    "01 / New analysis",
    "Radiograph intake",
    "Upload a chest radiograph and choose the language used for the patient-facing explanation.",
)

input_col, architecture_col = st.columns([1.08, 0.92], gap="large")

with input_col:
    uploaded = st.file_uploader(
        "Chest radiograph",
        type=["png", "jpg", "jpeg"],
        help="Supported formats: PNG, JPG, JPEG.",
    )

    language = st.selectbox(
        "Patient output language",
        SUPPORTED_LANGUAGES,
        index=0,
    )

    run = st.button(
        "Run clinical analysis  →",
        type="primary",
        use_container_width=True,
        disabled=uploaded is None,
    )

    if uploaded is not None:
        st.markdown(
            f"""
            <div class="ms-note">
                Selected study: <strong>{esc(uploaded.name)}</strong><br>
                Ready for analysis.
            </div>
            """,
            unsafe_allow_html=True,
        )

with architecture_col:
    if uploaded is None:
        render_workflow_panel()
    else:
        st.markdown(
            """
            <div class="ms-panel gold-edge" style="padding-bottom:.85rem;">
                <div class="ms-mini-label">Study preview</div>
                <div class="ms-panel-title" style="margin-top:.45rem;">Selected radiograph</div>
                <div class="ms-panel-copy">Review the image before running the analysis workflow.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.image(uploaded.getvalue(), caption=uploaded.name, use_container_width=True)


# -----------------------------------------------------------------------------
# Execute analysis
# -----------------------------------------------------------------------------
if run and uploaded is not None:
    outputs_dir = Path("outputs")
    outputs_dir.mkdir(parents=True, exist_ok=True)

    scan_name = Path(uploaded.name).name
    scan_path = outputs_dir / f"scan_{uuid.uuid4().hex[:10]}{safe_suffix(scan_name)}"
    scan_path.write_bytes(uploaded.getvalue())

    progress = st.progress(0, text="Preparing analysis workspace…")

    try:
        progress.progress(12, text="Radiograph secured. Starting agentic analysis…")
        with st.spinner("Running MedScribe clinical intelligence pipeline…"):
            result = run_agent(str(scan_path), language)

        progress.progress(76, text="Agent workflow complete. Generating explainability map…")
        findings, img_tensor = detect_abnormalities(str(scan_path))
        heatmap = generate_heatmap(str(scan_path), img_tensor)

        progress.progress(100, text="Analysis complete.")

        st.session_state.analysis_result = result
        st.session_state.analysis_findings = findings
        st.session_state.analysis_heatmap = heatmap
        st.session_state.analysis_scan_path = str(scan_path)
        st.session_state.analysis_scan_name = scan_name
        st.session_state.analysis_language = language

        st.success("Analysis completed successfully.")

    except Exception as exc:
        progress.empty()
        print(f"[MedScribe AI] Analysis error: {type(exc).__name__}: {exc}")
        st.error("The analysis could not be completed. Please verify the study and try again.")


# -----------------------------------------------------------------------------
# Results workspace
# -----------------------------------------------------------------------------
result = st.session_state.analysis_result
findings = st.session_state.analysis_findings
heatmap = st.session_state.analysis_heatmap
scan_path = st.session_state.analysis_scan_path
scan_name = st.session_state.analysis_scan_name
result_language = st.session_state.analysis_language

if result and scan_path:
    urgency = normalize_urgency(result.get("urgency"))
    escalated = bool(result.get("escalated", False))
    confidence = top_confidence(findings)

    section_header(
        "02 / Review",
        "Radiograph intelligence",
        "Compare the source study with the model attention map, then review the detected findings and confidence values.",
    )

    # Key result metrics
    st.markdown(
        f"""
        <div class="ms-metrics">
            <div class="ms-metric">
                <div class="ms-metric-label">Displayed findings</div>
                <div class="ms-metric-value">{len(findings):02d}</div>
                <div class="ms-metric-sub">Above the model display threshold</div>
            </div>
            <div class="ms-metric">
                <div class="ms-metric-label">Highest confidence</div>
                <div class="ms-metric-value">{confidence * 100:.1f}%</div>
                <div class="ms-metric-sub">Highest returned pathology score</div>
            </div>
            <div class="ms-metric">
                <div class="ms-metric-label">Triage status</div>
                <div class="ms-metric-value" style="text-transform:capitalize;">{esc(urgency)}</div>
                <div class="ms-metric-sub">Agent-assessed urgency class</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    source_col, cam_col = st.columns(2, gap="medium")
    with source_col:
        st.markdown(
            """
            <div class="ms-mini-label" style="margin-bottom:.55rem;">Source / original radiograph</div>
            """,
            unsafe_allow_html=True,
        )
        st.image(scan_path, caption="Original radiograph", use_container_width=True)

    with cam_col:
        st.markdown(
            """
            <div class="ms-mini-label" style="margin-bottom:.55rem;">Explainability / model attention</div>
            """,
            unsafe_allow_html=True,
        )
        st.image(heatmap, caption="Grad-CAM attention map", use_container_width=True)

    findings_col, urgency_col = st.columns([1.45, .75], gap="medium")
    with findings_col:
        render_findings(findings)
    with urgency_col:
        render_urgency(urgency, escalated)

    # Clinical report
    section_header(
        "03 / Clinical synthesis",
        "Structured report",
        "The report below is produced by the MedScribe clinical agent from the model findings.",
    )

    st.markdown(
        f"""
        <div class="ms-report-shell">
            <div class="ms-report-heading">
                <div>
                    <div class="ms-mini-label">Radiology output</div>
                    <div class="ms-report-title">Clinical report</div>
                </div>
                <div class="ms-report-meta">{esc(scan_name or 'Study')}</div>
            </div>
        </div>
        <div class="ms-report-marker"></div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(result.get("clinical_report") or "_No clinical report was returned by the agent._")

    # Patient communication and trace
    section_header(
        "04 / Communication & audit",
        "Patient summary and agent trace",
        "Review the patient-facing explanation and the sequence of tools selected by the agent.",
    )

    summary_tab, trace_tab = st.tabs(["Patient summary", "Agent workflow"])

    with summary_tab:
        patient_summary = result.get("patient_summary") or "No patient summary was returned by the agent."
        is_rtl = (result_language or "") in {"Urdu", "Arabic", "Persian"}
        direction = "rtl" if is_rtl else "ltr"
        st.markdown(
            f"""
            <div class="ms-summary-shell">
                <div class="ms-report-heading">
                    <div>
                        <div class="ms-mini-label">Patient communication</div>
                        <div class="ms-report-title">{esc(result_language or 'Selected language')}</div>
                    </div>
                    <div class="ms-report-meta">Plain-language output</div>
                </div>
                <div class="ms-summary-text" dir="{direction}">{esc(patient_summary)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with trace_tab:
        st.markdown(
            """
            <div class="ms-panel-copy" style="margin:0 0 .9rem;">
                Tool sequence returned by the MedScribe clinical agent for this analysis.
            </div>
            """,
            unsafe_allow_html=True,
        )
        render_trace(result.get("agent_trace") or [])

    # Export
    section_header(
        "05 / Export",
        "Session record",
        "Download a text snapshot of the generated findings, report, urgency and patient summary.",
    )

    export_col, note_col = st.columns([.72, 1.28], gap="large")
    with export_col:
        st.markdown('<div class="ms-dark-action"></div>', unsafe_allow_html=True)
        st.download_button(
            "Download analysis record",
            data=export_text(scan_name or "study", result_language or "", findings, result),
            file_name=f"medscribe_{Path(scan_name or 'study').stem}_report.txt",
            mime="text/plain",
            use_container_width=True,
        )
    with note_col:
        st.markdown(
            """
            <div class="ms-note" style="margin-top:0;">
                The session record contains the displayed findings, structured report, urgency status and patient summary
                for the current analysis.
            </div>
            """,
            unsafe_allow_html=True,
        )


# -----------------------------------------------------------------------------
# Footer
# -----------------------------------------------------------------------------
st.markdown(
    """
    <footer class="ms-footer">
        <div><strong>MedScribe AI</strong> · AI-assisted radiology intelligence</div>
        <div>
            Clinical review required · Generated outputs must not be used as a standalone diagnosis.
        </div>
    </footer>
    """,
    unsafe_allow_html=True,
)
