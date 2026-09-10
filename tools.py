from langchain_core.tools import tool
from vision import detect_abnormalities, generate_heatmap
from agent import generate_clinical_report, generate_patient_summary, detect_urgency

@tool
def detect_findings(image_path: str) -> dict:
    """Runs the CV model on the X-ray and returns detected pathologies
    with confidence scores."""
    findings, _ = detect_abnormalities(image_path)
    return {"findings": findings}

@tool
def assess_urgency(report: str) -> str:
    """Classifies the clinical report as 'routine', 'urgent', or 'critical'."""
    return detect_urgency(report)

@tool
def write_clinical_report(findings: list) -> str:
    """Generates a structured clinical radiology report from findings."""
    return generate_clinical_report(findings)

@tool
def write_patient_summary(report: str, language: str) -> str:
    """Rewrites the clinical report into plain language for the patient
    in their preferred language."""
    return generate_patient_summary(report, language)

@tool
def escalate_to_doctor(reason: str) -> str:
    """Sends an urgent alert to the on-call radiologist. Use only when
    urgency is 'critical'."""
    # For demo: just log it. In production: Slack/Twilio/email.
    print(f"[ALERT SENT] {reason}")
    return f"Alert sent: {reason}"

TOOLS = [
    detect_findings,
    assess_urgency,
    write_clinical_report,
    write_patient_summary,
    escalate_to_doctor,
]