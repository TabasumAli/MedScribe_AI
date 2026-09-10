import streamlit as st
import os
from vision import generate_heatmap, detect_abnormalities
from orchestrator import run_agent
from settings import SUPPORTED_LANGUAGES

st.set_page_config(page_title="MedScribe AI", layout="wide")
st.title("🩺 MedScribe AI")
st.caption("Agentic radiology assistant — reasons, reports, translates, escalates.")

# RTL support for Urdu/Arabic
st.markdown("""
<style>
    div[dir="rtl"] { font-family: 'Noto Nastaliq Urdu', 'Jameel Noori Nastaleeq', sans-serif;
                     font-size: 1.05rem; line-height: 2; }
</style>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1, 2])

with col1:
    uploaded = st.file_uploader("Upload scan", type=["png", "jpg", "jpeg"])
    language = st.selectbox("Patient language", SUPPORTED_LANGUAGES)
    run = st.button("Analyze", type="primary")

if run and uploaded:
    os.makedirs("outputs", exist_ok=True)
    path = f"outputs/{uploaded.name}"
    with open(path, "wb") as f:
        f.write(uploaded.read())

    with st.spinner("🧠 Agent is reasoning..."):
        result = run_agent(path, language)

    # Heatmap (still computed for visualization)
    _, img_tensor = detect_abnormalities(path)
    heatmap = generate_heatmap(path, img_tensor)

    with col2:
        st.subheader("📸 Scan + AI Attention")
        c1, c2 = st.columns(2)
        c1.image(path, caption="Original", use_container_width=True)
        c2.image(heatmap, caption="AI Heatmap", use_container_width=True)

    st.subheader("🧠 Agent Trace (what it decided to do)")
    for step in result["agent_trace"]:
        st.write(f"→ **{step['tool']}**  `{step['args']}`")

    st.subheader("📋 Clinical Report")
    st.write(result["clinical_report"])

    st.subheader("🚨 Urgency")
    urgency = result["urgency"]
    badge = {"routine": "🟢 Routine", "urgent": "🟡 Urgent", "critical": "🔴 Critical"}
    st.markdown(f"### {badge.get(urgency, urgency)}")
    if result["escalated"]:
        st.error("⚠️ Critical finding — alert escalated to on-call radiologist.")

    st.subheader(f"💬 Patient Summary ({language})")
    if language in ["Urdu", "Arabic", "Persian"]:
        st.markdown(
            f'<div dir="rtl" style="text-align:right;">{result["patient_summary"]}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.success(result["patient_summary"])