# app.py — MedScribe AI (Tabbed Layout)
from __future__ import annotations

import html
import json
import os
import uuid
from pathlib import Path
from typing import Any

import streamlit as st
from PIL import Image

from orchestrator import run_agent
from settings import SUPPORTED_LANGUAGES
from vision import detect_abnormalities, generate_heatmap


# ═══════════════════════════════════════════════════════════════
#  PAGE CONFIG
# ═══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="MedScribe AI",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ═══════════════════════════════════════════════════════════════
#  ROYAL CSS
# ═══════════════════════════════════════════════════════════════
ROYAL_CSS = r"""
<style>
:root {
    --bg-0: #050b14;
    --bg-1: #07111f;
    --surface-1: #0d1928;
    --surface-2: #101d30;
    --line: rgba(151, 169, 191, 0.18);
    --line-gold: rgba(215, 194, 154, 0.30);
    --ivory: #f5f1e8;
    --ivory-soft: #ddd7ca;
    --muted: #9aa8b9;
    --muted-2: #6f7d90;
    --gold: #b79a5b;
    --champagne: #d7c29a;
    --sapphire: #4169a8;
    --success: #58a889;
    --warning: #c79a54;
    --critical: #c75b64;
    --shadow: 0 20px 70px rgba(0, 0, 0, 0.30);
}

html, body, [class*="css"] {
    font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont,
        "Segoe UI", sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 82% 8%, rgba(65, 105, 168, 0.11), transparent 31rem),
        radial-gradient(circle at 17% 72%, rgba(183, 154, 91, 0.055), transparent 29rem),
        linear-gradient(145deg, #050b14 0%, #07111f 43%, #081523 100%);
    color: var(--ivory);
    overflow-x: hidden;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header[data-testid="stHeader"] {
    visibility: hidden;
}
[data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stStatusWidget"] {
    display: none !important;
}

.block-container {
    max-width: 1480px;
    padding-top: 1rem;
    padding-bottom: 3rem;
}

/* ── Top bar ────────────────────────────────────────────── */
.ms-topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    padding: .75rem .2rem 1.15rem .2rem;
    border-bottom: 1px solid rgba(215,194,154,.12);
    margin-bottom: 1.4rem;
}
.ms-brand { display: flex; align-items: center; gap: .85rem; }
.ms-monogram {
    width: 2.55rem; height: 2.55rem;
    display: grid; place-items: center;
    border: 1px solid rgba(215,194,154,.48);
    background: linear-gradient(145deg, rgba(215,194,154,.08), rgba(65,105,168,.045));
    color: var(--champagne);
    font-family: "Iowan Old Style", "Palatino Linotype", Georgia, serif;
    font-size: 1rem; letter-spacing: .08em;
}
.ms-brand-name {
    font-family: "Iowan Old Style", "Palatino Linotype", Georgia, serif;
    color: var(--ivory); font-size: 1.17rem; letter-spacing: .035em; line-height: 1.05;
}
.ms-brand-meta {
    margin-top: .22rem; color: var(--muted-2);
    font-size: .62rem; letter-spacing: .18em; text-transform: uppercase;
}
.ms-system {
    display: flex; align-items: center; gap: .58rem;
    color: #aab6c5; font-size: .68rem; letter-spacing: .12em; text-transform: uppercase;
}
.ms-system-dot {
    width: .48rem; height: .48rem; border-radius: 50%;
    background: var(--success);
    box-shadow: 0 0 0 0 rgba(88,168,137,.28);
    animation: msPulse 2.4s ease-in-out infinite;
}
@keyframes msPulse {
    0%, 100% { box-shadow: 0 0 0 0 rgba(88,168,137,.28); }
    50% { box-shadow: 0 0 0 7px rgba(88,168,137,0); }
}

/* ── Native Tabs restyle ────────────────────────────────── */
[data-baseweb="tab-list"] {
    gap: .35rem !important;
    border-bottom: 1px solid rgba(151,169,191,.12) !important;
    margin-bottom: 1.2rem;
}
button[data-baseweb="tab"] {
    min-height: 2.9rem !important;
    padding: 0 1.1rem !important;
    border-radius: 0 !important;
    color: #7f8da0 !important;
    font-size: .68rem !important;
    font-weight: 680 !important;
    letter-spacing: .10em !important;
    text-transform: uppercase;
    background: transparent !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: var(--ivory) !important;
}
[data-baseweb="tab-highlight"] {
    background: var(--champagne) !important;
    height: 1px !important;
}
[data-baseweb="tab-border"] { background: transparent !important; }

/* ── Section headings ──────────────────────────────────── */
.ms-eyebrow {
    color: var(--champagne);
    font-size: .68rem; font-weight: 650;
    letter-spacing: .18em; text-transform: uppercase;
    margin-bottom: .3rem;
}
.ms-h1 {
    font-family: "Iowan Old Style", "Palatino Linotype", Georgia, serif;
    color: var(--ivory);
    font-size: 1.9rem;
    letter-spacing: -.03em;
    margin: 0 0 .35rem;
}
.ms-sub {
    color: var(--muted);
    font-size: .82rem;
    line-height: 1.6;
    margin-bottom: 1.4rem;
}

/* ── Panels ────────────────────────────────────────────── */
.ms-panel {
    border: 1px solid rgba(151,169,191,.14);
    background: linear-gradient(145deg, rgba(16,29,48,.66), rgba(10,21,36,.72));
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    box-shadow: 0 14px 55px rgba(0,0,0,.15);
    padding: 1.3rem 1.4rem;
    margin-bottom: 1rem;
}
.ms-panel.gold-edge { border-top-color: rgba(215,194,154,.42); }
.ms-panel-title {
    color: var(--ivory);
    font-size: .82rem; font-weight: 690;
    letter-spacing: .06em; text-transform: uppercase;
    margin-bottom: .5rem;
}
.ms-panel-copy {
    color: var(--muted);
    font-size: .78rem;
    line-height: 1.65;
}

/* ── Urgency badge ─────────────────────────────────────── */
.ms-badge {
    display: inline-block;
    padding: .5rem 1.1rem;
    border-radius: 999px;
    font-weight: 700;
    font-size: .82rem;
    letter-spacing: .12em;
    text-transform: uppercase;
}
.ms-badge-routine  { background: rgba(88,168,137,.15); color: #7dd3b0; border: 1px solid rgba(88,168,137,.4); }
.ms-badge-urgent   { background: rgba(199,154,84,.15); color: #e5c88f; border: 1px solid rgba(199,154,84,.4); }
.ms-badge-critical { background: rgba(199,91,100,.15); color: #f0a5ac; border: 1px solid rgba(199,91,100,.4); }

.ms-critical-alert {
    margin-top: .8rem;
    border-left: 3px solid var(--critical);
    background: rgba(199,91,100,.07);
    padding: .85rem 1rem;
    color: #cbb1b4;
    font-size: .78rem;
    line-height: 1.6;
}

/* ── Findings ──────────────────────────────────────────── */
.ms-finding-row {
    padding: .8rem 0;
    border-bottom: 1px solid rgba(151,169,191,.08);
}
.ms-finding-row:last-child { border-bottom: 0; }
.ms-finding-head {
    display: flex; justify-content: space-between;
    margin-bottom: .5rem; gap: 1rem;
}
.ms-finding-name { color: #dce1e8; font-size: .82rem; font-weight: 620; }
.ms-finding-score {
    color: var(--champagne);
    font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
    font-size: .72rem;
}
.ms-track {
    height: 5px;
    background: rgba(151,169,191,.09);
    overflow: hidden;
    border-radius: 3px;
}
.ms-fill {
    height: 100%;
    background: linear-gradient(90deg, #345c94, #708db7 68%, #b79a5b 100%);
    transition: width .8s cubic-bezier(.2,.8,.2,1);
}

/* ── Trace items ───────────────────────────────────────── */
.ms-trace-item {
    display: grid;
    grid-template-columns: 2.4rem 1fr;
    gap: .85rem;
    padding: .15rem 0 1.05rem;
    position: relative;
}
.ms-trace-item:not(:last-child)::after {
    content: "";
    position: absolute;
    left: 1.16rem; top: 2.15rem; bottom: .1rem;
    width: 1px;
    background: linear-gradient(to bottom, rgba(215,194,154,.30), rgba(151,169,191,.08));
}
.ms-trace-no {
    width: 2.35rem; height: 2.35rem;
    display: grid; place-items: center;
    border: 1px solid rgba(215,194,154,.22);
    color: var(--champagne);
    font-family: "Iowan Old Style", "Palatino Linotype", Georgia, serif;
    font-size: .78rem;
    background: rgba(183,154,91,.025);
}
.ms-trace-tool {
    color: #d7dde5; font-size: .74rem; font-weight: 690;
    letter-spacing: .06em; text-transform: uppercase;
}
.ms-trace-desc {
    margin-top: .2rem; color: #7f8da0;
    font-size: .68rem; line-height: 1.55;
}
.ms-trace-args {
    margin-top: .35rem; color: #8492a4;
    font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
    font-size: .6rem; word-break: break-word;
}

/* ── Patient summary ───────────────────────────────────── */
.ms-summary-text {
    color: #c8d0da;
    font-size: .9rem;
    line-height: 1.85;
    white-space: pre-wrap;
}
.ms-summary-text[dir="rtl"] {
    font-family: "Noto Nastaliq Urdu", "Noto Naskh Arabic", "Segoe UI", sans-serif;
    font-size: 1.05rem;
    line-height: 2.1;
    text-align: right;
}

/* ── Metrics ───────────────────────────────────────────── */
.ms-metrics {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: .8rem;
    margin: 1rem 0 1.5rem;
}
.ms-metric {
    border: 1px solid rgba(151,169,191,.14);
    background: linear-gradient(145deg, rgba(16,29,48,.66), rgba(10,21,36,.72));
    padding: 1rem 1.1rem;
}
.ms-metric-label {
    color: var(--muted-2);
    font-size: .6rem; letter-spacing: .15em;
    text-transform: uppercase;
}
.ms-metric-value {
    margin-top: .35rem;
    color: var(--ivory);
    font-family: "Iowan Old Style", "Palatino Linotype", Georgia, serif;
    font-size: 1.7rem;
}

/* ── Buttons ───────────────────────────────────────────── */
.stButton > button, .stDownloadButton > button {
    min-height: 3rem;
    border-radius: 4px !important;
    font-weight: 700 !important;
    letter-spacing: .08em;
    text-transform: uppercase;
    font-size: .72rem !important;
    transition: transform .2s ease, box-shadow .2s ease;
}
.stButton > button[kind="primary"], button[data-testid="stBaseButton-primary"] {
    background: linear-gradient(100deg, #A98642 0%, #B79A5B 42%, #D7C29A 100%) !important;
    color: #07111F !important;
    border: 1px solid rgba(231,208,158,.78) !important;
    box-shadow: 0 12px 30px rgba(183,154,91,.18) !important;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 16px 38px rgba(183,154,91,.28) !important;
}

/* ── File uploader ─────────────────────────────────────── */
[data-testid="stFileUploader"] > label,
[data-testid="stSelectbox"] > label {
    color: #a7b2c0 !important;
    font-size: .70rem !important;
    letter-spacing: .10em;
    text-transform: uppercase;
    font-weight: 620;
}
[data-testid="stFileUploaderDropzone"] {
    min-height: 10rem;
    border: 1px solid rgba(215,194,154,.20) !important;
    border-radius: 7px !important;
    background: linear-gradient(rgba(13,25,40,.67), rgba(10,20,33,.72)) !important;
}
[data-testid="stFileUploaderDropzone"]:hover {
    border-color: rgba(215,194,154,.45) !important;
}

div[data-baseweb="select"] > div {
    min-height: 3rem;
    background: linear-gradient(145deg, rgba(16,29,48,.72), rgba(11,23,40,.76)) !important;
    border: 1px solid rgba(151,169,191,.17) !important;
    border-radius: 5px !important;
    color: var(--ivory) !important;
}
ul[role="listbox"] { background: #0d1928 !important; }
li[role="option"] { color: #e6e1d8 !important; }

/* ── Image frames ──────────────────────────────────────── */
[data-testid="stImage"] {
    border: 1px solid rgba(151,169,191,.14);
    background: #04080d;
}
[data-testid="stImageCaption"] {
    color: #7f8da0 !important;
    font-size: .64rem !important;
    letter-spacing: .11em;
    text-transform: uppercase;
}

/* ── Empty state ───────────────────────────────────────── */
.ms-empty {
    text-align: center;
    padding: 4rem 2rem;
    border: 1px dashed rgba(151,169,191,.20);
    border-radius: 8px;
    color: var(--muted);
}
.ms-empty-icon { font-size: 3rem; margin-bottom: 1rem; opacity: .5; }
.ms-empty-title {
    color: var(--ivory);
    font-family: "Iowan Old Style", "Palatino Linotype", Georgia, serif;
    font-size: 1.3rem;
    margin-bottom: .5rem;
}
.ms-empty-copy { font-size: .82rem; line-height: 1.65; }

/* ── Footer ────────────────────────────────────────────── */
.ms-footer {
    margin-top: 3rem;
    padding-top: 1.15rem;
    border-top: 1px solid rgba(215,194,154,.11);
    display: flex;
    justify-content: space-between;
    gap: 1.3rem;
    color: #627186;
    font-size: .62rem;
    line-height: 1.65;
}
.ms-footer strong { color: #8794a6; font-weight: 650; }

/* ── Responsive ────────────────────────────────────────── */
@media (max-width: 900px) {
    .block-container { padding-left: 1rem; padding-right: 1rem; }
    .ms-metrics { grid-template-columns: 1fr; }
    .ms-footer { flex-direction: column; }
}
</style>
"""
st.markdown(ROYAL_CSS, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════
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
    return {
        "detect_findings": "Vision inference · DenseNet121 pathology screening",
        "write_clinical_report": "Clinical synthesis · structured radiology report",
        "assess_urgency": "Triage layer · routine / urgent / critical classification",
        "write_patient_summary": "Communication layer · patient-friendly language output",
        "escalate_to_doctor": "Escalation layer · on-call radiologist alert",
        "verify_report_quality": "Quality verification · self-review of report",
    }.get(tool_name, "Agent tool execution")


def compact_args(args: Any, limit: int = 200) -> str:
    try:
        text = json.dumps(args, ensure_ascii=False, default=str)
    except Exception:
        text = str(args)
    text = " ".join(text.split())
    return text if len(text) <= limit else text[: limit - 1] + "…"


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


def render_empty_state(icon: str, title: str, copy: str) -> None:
    st.markdown(
        f"""
        <div class="ms-empty">
            <div class="ms-empty-icon">{icon}</div>
            <div class="ms-empty-title">{esc(title)}</div>
            <div class="ms-empty-copy">{esc(copy)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════
#  SESSION STATE
# ═══════════════════════════════════════════════════════════════
DEFAULTS = {
    "result": None,
    "findings": [],
    "heatmap": None,
    "scan_path": None,
    "scan_name": None,
    "language": "English",
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ═══════════════════════════════════════════════════════════════
#  HEADER
# ═══════════════════════════════════════════════════════════════
render_topbar()


# ═══════════════════════════════════════════════════════════════
#  TABS
# ═══════════════════════════════════════════════════════════════
tab_upload, tab_diag, tab_trace, tab_patient, tab_export = st.tabs(
    ["📤 Upload", "🩺 Diagnosis", "🧠 Agent Trace", "💬 Patient", "📥 Export"]
)


# ─────────────────────────────────────────────────────────────
#  TAB 1 — UPLOAD
# ─────────────────────────────────────────────────────────────
with tab_upload:
    st.markdown('<div class="ms-eyebrow">Step 01 / New Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="ms-h1">Radiograph intake</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="ms-sub">Upload a chest radiograph and select the language for the patient-facing explanation.</div>',
        unsafe_allow_html=True,
    )

    up_col, prev_col = st.columns([1.05, 0.95], gap="large")

    with up_col:
        uploaded = st.file_uploader(
            "Chest radiograph",
            type=["png", "jpg", "jpeg"],
            help="Supported formats: PNG, JPG, JPEG.",
        )

        st.session_state.language = st.selectbox(
            "Patient output language",
            SUPPORTED_LANGUAGES,
            index=SUPPORTED_LANGUAGES.index(st.session_state.language)
            if st.session_state.language in SUPPORTED_LANGUAGES
            else 0,
        )

        run = st.button(
            "Run clinical analysis →",
            type="primary",
            use_container_width=True,
            disabled=uploaded is None,
        )

        if uploaded is not None:
            st.markdown(
                f"""
                <div class="ms-panel" style="margin-top:1rem;">
                    <div class="ms-panel-title">Selected study</div>
                    <div class="ms-panel-copy">{esc(uploaded.name)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with prev_col:
        if uploaded is None:
            render_empty_state(
                "🩻",
                "No scan selected",
                "Upload a chest X-ray on the left to preview it here before running the analysis.",
            )
        else:
            st.markdown(
                '<div class="ms-eyebrow" style="margin-bottom:.6rem;">Preview</div>',
                unsafe_allow_html=True,
            )
            try:
                preview_img = Image.open(uploaded)
                st.image(preview_img, caption=uploaded.name, use_container_width=True)
            except Exception:
                st.image(uploaded, caption=uploaded.name, use_container_width=True)


# ─────────────────────────────────────────────────────────────
#  RUN ANALYSIS (only once, outside tabs)
# ─────────────────────────────────────────────────────────────
if run and uploaded is not None:
    outputs_dir = Path("outputs")
    outputs_dir.mkdir(parents=True, exist_ok=True)

    scan_name = Path(uploaded.name).name
    scan_path = outputs_dir / f"scan_{uuid.uuid4().hex[:10]}{safe_suffix(scan_name)}"
    scan_path.write_bytes(uploaded.getvalue())

    progress = st.progress(0, text="Preparing analysis workspace…")

    try:
        progress.progress(15, text="Radiograph secured. Starting agentic analysis…")
        result = run_agent(str(scan_path), st.session_state.language)

        progress.progress(75, text="Agent workflow complete. Generating explainability map…")
        findings, img_tensor = detect_abnormalities(str(scan_path))
        heatmap = generate_heatmap(str(scan_path), img_tensor)

        progress.progress(100, text="Analysis complete.")

        st.session_state.result = result
        st.session_state.findings = findings
        st.session_state.heatmap = heatmap
        st.session_state.scan_path = str(scan_path)
        st.session_state.scan_name = scan_name

        st.success("✅ Analysis completed. Check the other tabs.")

    except Exception as exc:
        progress.empty()
        print(f"[MedScribe AI] Analysis error: {type(exc).__name__}: {exc}")
        st.error("The analysis could not be completed. Please verify the study and try again.")


# ─────────────────────────────────────────────────────────────
#  TAB 2 — DIAGNOSIS
# ─────────────────────────────────────────────────────────────
with tab_diag:
    if st.session_state.result is None:
        render_empty_state(
            "🩺",
            "No analysis yet",
            "Run an analysis from the Upload tab to see the diagnosis here.",
        )
    else:
        result = st.session_state.result
        findings = st.session_state.findings
        heatmap = st.session_state.heatmap
        scan_path = st.session_state.scan_path
        urgency = normalize_urgency(result.get("urgency"))
        escalated = bool(result.get("escalated", False))
        confidence = top_confidence(findings)

        st.markdown('<div class="ms-eyebrow">Step 02 / Review</div>', unsafe_allow_html=True)
        st.markdown('<div class="ms-h1">Radiograph intelligence</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="ms-sub">Compare the source study with the AI attention map, then review detected findings and urgency.</div>',
            unsafe_allow_html=True,
        )

        # Metrics
        st.markdown(
            f"""
            <div class="ms-metrics">
                <div class="ms-metric">
                    <div class="ms-metric-label">Displayed findings</div>
                    <div class="ms-metric-value">{len(findings):02d}</div>
                </div>
                <div class="ms-metric">
                    <div class="ms-metric-label">Highest confidence</div>
                    <div class="ms-metric-value">{confidence * 100:.1f}%</div>
                </div>
                <div class="ms-metric">
                    <div class="ms-metric-label">Triage status</div>
                    <div class="ms-metric-value" style="text-transform:capitalize;">{esc(urgency)}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Images
        img1, img2 = st.columns(2, gap="medium")
        with img1:
            st.image(scan_path, caption="Original radiograph", use_container_width=True)
        with img2:
            st.image(heatmap, caption="Grad-CAM attention map", use_container_width=True)

        # Urgency + Findings
        st.markdown('<div class="ms-eyebrow" style="margin-top:1.5rem;">Triage</div>', unsafe_allow_html=True)
        badge_map = {
            "routine": ("ms-badge-routine", "🟢 Routine"),
            "urgent": ("ms-badge-urgent", "🟡 Urgent"),
            "critical": ("ms-badge-critical", "🔴 Critical"),
        }
        badge_class, badge_text = badge_map.get(urgency, badge_map["routine"])
        st.markdown(
            f'<div class="ms-panel"><span class="ms-badge {badge_class}">{badge_text}</span></div>',
            unsafe_allow_html=True,
        )
        if escalated:
            st.markdown(
                '<div class="ms-critical-alert">⚠️ Critical finding — alert escalated to on-call radiologist.</div>',
                unsafe_allow_html=True,
            )

        # Findings bars
        st.markdown('<div class="ms-eyebrow" style="margin-top:1.5rem;">Detected findings</div>', unsafe_allow_html=True)
        if not findings:
            st.markdown(
                '<div class="ms-panel"><div class="ms-panel-copy">No pathology exceeded the display threshold.</div></div>',
                unsafe_allow_html=True,
            )
        else:
            sorted_findings = sorted(
                findings,
                key=lambda x: float(x.get("confidence", 0) or 0),
                reverse=True,
            )
            rows = []
            for item in sorted_findings:
                label = esc(item.get("label", "Finding"))
                conf = max(0.0, min(1.0, float(item.get("confidence", 0) or 0)))
                pct = conf * 100
                rows.append(
                    f'<div class="ms-finding-row">'
                    f'<div class="ms-finding-head">'
                    f'<div class="ms-finding-name">{label}</div>'
                    f'<div class="ms-finding-score">{pct:.1f}%</div>'
                    f'</div>'
                    f'<div class="ms-track"><div class="ms-fill" style="width:{pct:.1f}%"></div></div>'
                    f'</div>'
                )
            st.markdown(f'<div class="ms-panel">{"".join(rows)}</div>', unsafe_allow_html=True)

        # Clinical report
        st.markdown('<div class="ms-eyebrow" style="margin-top:1.5rem;">Clinical report</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="ms-panel gold-edge">{result.get("clinical_report") or "No report returned."}</div>',
            unsafe_allow_html=True,
        )


# ─────────────────────────────────────────────────────────────
#  TAB 3 — AGENT TRACE
# ─────────────────────────────────────────────────────────────
with tab_trace:
    if st.session_state.result is None:
        render_empty_state(
            "🧠",
            "No agent trace yet",
            "Run an analysis to see which tools the agent decided to call.",
        )
    else:
        result = st.session_state.result
        trace = result.get("agent_trace") or []

        st.markdown('<div class="ms-eyebrow">Step 03 / Agent Audit</div>', unsafe_allow_html=True)
        st.markdown('<div class="ms-h1">Agent reasoning path</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="ms-sub">This shows exactly which tools the agent decided to call, in what order, and with what inputs.</div>',
            unsafe_allow_html=True,
        )

        if not trace:
            st.markdown('<div class="ms-panel">No tool trace was returned for this run.</div>', unsafe_allow_html=True)
        else:
            items = []
            for idx, step in enumerate(trace, start=1):
                tool = str(step.get("tool", "agent_step"))
                args = compact_args(step.get("args", {}))
                items.append(
                    f'<div class="ms-trace-item">'
                    f'<div class="ms-trace-no">{idx:02d}</div>'
                    f'<div>'
                    f'<div class="ms-trace-tool">{esc(tool.replace("_", " "))}</div>'
                    f'<div class="ms-trace-desc">{esc(trace_description(tool))}</div>'
                    f'<div class="ms-trace-args">{esc(args)}</div>'
                    f'</div>'
                    f'</div>'
                )
            st.markdown(f'<div class="ms-panel">{"".join(items)}</div>', unsafe_allow_html=True)

        with st.expander("🤖 Final agent message"):
            st.write(result.get("final_message", "—"))


# ─────────────────────────────────────────────────────────────
#  TAB 4 — PATIENT VIEW
# ─────────────────────────────────────────────────────────────
with tab_patient:
    if st.session_state.result is None:
        render_empty_state(
            "💬",
            "No patient summary yet",
            "Run an analysis to see the plain-language explanation.",
        )
    else:
        result = st.session_state.result
        language = st.session_state.language
        summary = result.get("patient_summary") or "No patient summary returned."

        st.markdown('<div class="ms-eyebrow">Step 04 / Patient Communication</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="ms-h1">{esc(language)}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="ms-sub">A plain-language summary of the scan, written for the patient.</div>',
            unsafe_allow_html=True,
        )

        is_rtl = language in {"Urdu", "Arabic", "Persian"}
        direction = "rtl" if is_rtl else "ltr"
        st.markdown(
            f'<div class="ms-panel"><div class="ms-summary-text" dir="{direction}">{esc(summary)}</div></div>',
            unsafe_allow_html=True,
        )


# ─────────────────────────────────────────────────────────────
#  TAB 5 — EXPORT
# ─────────────────────────────────────────────────────────────
with tab_export:
    if st.session_state.result is None:
        render_empty_state(
            "📥",
            "Nothing to export yet",
            "Run an analysis to download a record.",
        )
    else:
        result = st.session_state.result
        findings = st.session_state.findings
        scan_name = st.session_state.scan_name or "study"
        language = st.session_state.language

        st.markdown('<div class="ms-eyebrow">Step 05 / Export</div>', unsafe_allow_html=True)
        st.markdown('<div class="ms-h1">Session record</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="ms-sub">Download a text snapshot of the findings, report, urgency and patient summary.</div>',
            unsafe_allow_html=True,
        )

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
        record = f"""MEDSCRIBE AI — RADIOLOGY INTELLIGENCE
AI-assisted radiology analysis

SCAN
File: {scan_name}
Patient output language: {language}

MODEL FINDINGS
{chr(10).join(finding_lines)}

CLINICAL REPORT
{result.get("clinical_report") or "No report returned."}

URGENCY
{urgency.upper()}

PATIENT SUMMARY
{result.get("patient_summary") or "No patient summary returned."}

DISCLAIMER
This AI-assisted output requires qualified clinical review and is not a standalone diagnosis.
"""

        st.download_button(
            "📥 Download analysis record",
            data=record,
            file_name=f"medscribe_{Path(scan_name).stem}_report.txt",
            mime="text/plain",
            use_container_width=True,
        )

        with st.expander("Preview record"):
            st.code(record, language="text")


# ═══════════════════════════════════════════════════════════════
#  FOOTER
# ═══════════════════════════════════════════════════════════════
st.markdown(
    """
    <footer class="ms-footer">
        <div><strong>MedScribe AI</strong> · AI-assisted radiology intelligence</div>
        <div>Clinical review required · Not a standalone diagnosis.</div>
    </footer>
    """,
    unsafe_allow_html=True,
)