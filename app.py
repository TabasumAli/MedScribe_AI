import streamlit as st
from PIL import Image
import os
from vision import detect_abnormalities, generate_heatmap
from agent import generate_clinical_report, generate_patient_summary, detect_urgency
from settings import SUPPORTED_LANGUAGES

st.set_page_config(page_title="MedScribe AI", layout="wide")
st.title("🩺 MedScribe AI")
st.caption("Agentic radiology assistant — detects, explains, reports, translates.")

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

    with st.spinner("Detecting abnormalities..."):
        findings, img_tensor = detect_abnormalities(path)
        heatmap = generate_heatmap(path, img_tensor)

    with st.spinner("Writing report..."):
        report = generate_clinical_report(findings)
        urgency = detect_urgency(report)
        summary = generate_patient_summary(report, language)

    with col2:
        st.subheader("📸 Scan + AI Attention")
        c1, c2 = st.columns(2)
        c1.image(path, caption="Original", use_container_width=True)
        c2.image(heatmap, caption="AI Heatmap", use_container_width=True)

    st.subheader("📋 Clinical Report")
    st.write(report)

    st.subheader("🧠 Detected Findings")
    for f in findings:
        st.write(f"• **{f['label']}** — {f['confidence']*100:.1f}%")

    badge = {"routine": "🟢 Routine", "urgent": "🟡 Urgent", "critical": "🔴 Critical"}
    st.subheader("🚨 Urgency")
    st.markdown(f"### {badge[urgency]}")
    if urgency == "critical":
        st.error("⚠️ Critical finding — escalation alert sent.")

    st.subheader(f"💬 Patient Summary ({language})")
    st.success(summary)
