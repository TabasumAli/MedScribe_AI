# specialist_agents.py
"""
Specialist sub-agents for the MedScribe multi-agent system.

Each agent is a small ReAct agent focused on ONE task:
- Detector Agent    → runs the CV model, interprets findings
- Reporter Agent    → writes clinical + patient reports
- Translator Agent  → creates the patient summary in the target language
"""

from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from settings import GROQ_API_KEY, LLM_MODEL
from tools import (
    detect_findings,
    write_clinical_report,
    assess_urgency,
    write_patient_summary,
)


# ─────────────────────────────────────────────────────────────
#  Shared LLM (used by all specialists)
# ─────────────────────────────────────────────────────────────
_llm = ChatGroq(
    api_key=GROQ_API_KEY,
    model=LLM_MODEL,
    temperature=0.1,
)


# ─────────────────────────────────────────────────────────────
#  DETECTOR AGENT — CV model only
# ─────────────────────────────────────────────────────────────
DETECTOR_PROMPT = """You are the Detector Agent. Your ONLY job:
1. Call detect_findings on the given image path.
2. Report the findings back clearly with confidence scores.

Do NOT write reports. Do NOT assess urgency. Just detect and report.
"""

detector_agent = create_react_agent(
    model=_llm,
    tools=[detect_findings],
    prompt=DETECTOR_PROMPT,
)


# ─────────────────────────────────────────────────────────────
#  REPORTER AGENT — clinical report + urgency
# ─────────────────────────────────────────────────────────────
REPORTER_PROMPT = """You are the Reporter Agent. Your job:
1. Given the findings, call write_clinical_report to generate a structured report.
2. Call assess_urgency on the report to determine urgency level.
3. Return the clinical report and urgency clearly.

Do NOT call detect_findings — findings are already provided.
"""

reporter_agent = create_react_agent(
    model=_llm,
    tools=[write_clinical_report, assess_urgency],
    prompt=REPORTER_PROMPT,
)


# ─────────────────────────────────────────────────────────────
#  TRANSLATOR AGENT — patient summary
# ─────────────────────────────────────────────────────────────
TRANSLATOR_PROMPT = """You are the Translator Agent. Your job:
1. Given the clinical report and target language, call write_patient_summary.
2. Return the plain-language summary in that language.

Do NOT write clinical reports. Do NOT assess urgency.
"""

translator_agent = create_react_agent(
    model=_llm,
    tools=[write_patient_summary],
    prompt=TRANSLATOR_PROMPT,
)


# ─────────────────────────────────────────────────────────────
#  Helper — run a sub-agent and return its final message
# ─────────────────────────────────────────────────────────────
def run_specialist(agent, task: str) -> dict:
    """Run a specialist agent on a task. Return all messages + final output."""
    result = agent.invoke(
        {"messages": [{"role": "user", "content": task}]},
        config={"recursion_limit": 20},
    )
    return {
        "messages": result["messages"],
        "final": result["messages"][-1].content,
    }