from groq import Groq
from settings import GROQ_API_KEY, LLM_MODEL
from prompts import CLINICAL_REPORT_PROMPT, PATIENT_SUMMARY_PROMPT

client = Groq(api_key=GROQ_API_KEY)

def generate_clinical_report(findings: list) -> str:
    prompt = CLINICAL_REPORT_PROMPT.format(findings=findings)
    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    return response.choices[0].message.content

def generate_patient_summary(report: str, language: str) -> str:
    prompt = PATIENT_SUMMARY_PROMPT.format(report=report, language=language)
    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    return response.choices[0].message.content

def detect_urgency(report: str) -> str:
    text = report.lower()
    if any(w in text for w in ["critical", "emergency", "immediate", "hemorrhage"]):
        return "critical"
    if any(w in text for w in ["urgent", "follow-up", "concerning"]):
        return "urgent"
    return "routine"