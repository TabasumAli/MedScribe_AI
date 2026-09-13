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


@tool
def verify_report_quality(clinical_report: str, findings: list) -> str:
    """Use this to verify your own report before finishing.

    Check:
    - Are all detected findings mentioned in the report?
    - Is the urgency level clearly stated?
    - Are there any claims not backed by the CV output?

    Return 'PASS' if the report is complete, or
    'NEEDS_REVISION: <reason>' if it needs fixing.
    """
    issues = []
    report_lower = clinical_report.lower() if clinical_report else ""

    # Check 1: every finding is mentioned
    if findings:
        for f in findings:
            label = f.get("label", "") if isinstance(f, dict) else str(f)
            if label and label.lower() not in report_lower:
                issues.append(f"Finding not mentioned: {label}")

    # Check 2: urgency is stated
    urgency_words = ["urgency", "urgent", "routine", "critical"]
    if not any(w in report_lower for w in urgency_words):
        issues.append("Urgency not stated in report")

    # Check 3: report is not empty
    if len(report_lower.strip()) < 50:
        issues.append("Report is too short")

    if issues:
        return f"NEEDS_REVISION: {'; '.join(issues)}"
    return "PASS"

@tool
def verify_report_quality(clinical_report: str, findings: list = None) -> str:
    """Verify that a clinical report is complete and accurate."""
    issues = []
    report_lower = (clinical_report or "").lower()
    
    if len(report_lower.strip()) < 50:
        issues.append("Report is too short")
    if not any(w in report_lower for w in ["urgency", "urgent", "routine", "critical"]):
        issues.append("Urgency not stated")
    if findings and isinstance(findings, list):
        for f in findings:
            label = f.get("label", "") if isinstance(f, dict) else str(f)
            if label and label.lower() not in report_lower:
                issues.append(f"Missing finding: {label}")
    
    if issues:
        return f"NEEDS_REVISION: {'; '.join(issues)}"
    return "PASS"

TOOLS = [
    detect_findings,
    assess_urgency,
    write_clinical_report,
    write_patient_summary,
    escalate_to_doctor,
    verify_report_quality,
]
