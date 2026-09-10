CLINICAL_REPORT_PROMPT = """
You are a radiology AI assistant. Given these findings from a scan:

{findings}

Write a structured clinical report with:
1. FINDINGS: Describe each abnormality with confidence.
2. IMPRESSION: Your overall interpretation.
3. RECOMMENDATION: Next steps.
4. URGENCY: One of "routine", "urgent", or "critical".
5. REASONING: Why you reached this conclusion.

Be concise and clinical.
"""

PATIENT_SUMMARY_PROMPT = """
Rewrite this clinical report in simple, kind, jargon-free language
for a patient with no medical background. Write it in {language}.

Clinical report:
{report}

Keep it under 150 words. Reassure where appropriate, but be honest.
"""