# orchestrator.py
"""
MedScribe AI — Multi-Agent Supervisor

The supervisor decides which specialist agents to invoke and in what order.
Each specialist is a focused ReAct agent:

  Detector Agent  → runs CV model
  Reporter Agent  → writes clinical report + urgency
  Translator Agent → writes patient summary in target language

The supervisor may run them in sequence, skip some, or loop back if quality is low.
"""

from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from settings import GROQ_API_KEY, LLM_MODEL
from tools import escalate_to_doctor, verify_report_quality
from specialist_agents import (
    detector_agent,
    reporter_agent,
    translator_agent,
    run_specialist,
)

# ─────────────────────────────────────────────────────────────
#  Supervisor LLM
# ─────────────────────────────────────────────────────────────
_supervisor_llm = ChatGroq(
    api_key=GROQ_API_KEY,
    model=LLM_MODEL,
    temperature=0.1,
)


SUPERVISOR_PROMPT = """You are the MedScribe Supervisor Agent.

Your goal: produce a complete radiology analysis for the chest X-ray.

You coordinate 3 specialist agents and use 2 tools:

SPECIALISTS (called via delegate_to_<name>):
- detector: runs the CV model, returns findings with confidence scores
- reporter: writes the clinical report + urgency assessment
- translator: writes the plain-language patient summary in a target language

TOOLS:
- escalate_to_doctor: sends an urgent alert to the on-call doctor
- verify_report_quality: verifies the clinical report is complete

YOUR WORKFLOW (you decide the order based on what you learn):

1. Ask the detector to analyze the image
2. Ask the reporter to write the clinical report using the findings
3. Ask the translator to write the patient summary in the target language
4. Call verify_report_quality to check the report
5. If urgency is critical, call escalate_to_doctor
6. When everything is done, summarize what you did

Think step by step. If a specialist returns incomplete output, ask them to redo it.
"""


# ─────────────────────────────────────────────────────────────
#  Delegation tools — supervisor calls these to invoke specialists
# ─────────────────────────────────────────────────────────────
from langchain_core.tools import tool


@tool
def delegate_to_detector(image_path: str) -> str:
    """Ask the Detector Agent to analyze the X-ray at image_path and return findings."""
    result = run_specialist(detector_agent, f"Analyze this image: {image_path}")
    return result["final"]


@tool
def delegate_to_reporter(findings: str) -> str:
    """Ask the Reporter Agent to write a clinical report from the given findings."""
    result = run_specialist(
        reporter_agent, f"Write a clinical report for these findings:\n{findings}"
    )
    return result["final"]


@tool
def delegate_to_translator(report: str, language: str) -> str:
    """Ask the Translator Agent to write a plain-language patient summary.

    Args:
        report: The clinical report text to translate.
        language: The target language (e.g., English, Urdu, Spanish, Arabic, Hindi).
    """
    task = (
        f"Write a plain-language patient summary in {language}.\n\n"
        f"Clinical report:\n{report}"
    )
    result = run_specialist(translator_agent, task)
    return result["final"]


SUPERVISOR_TOOLS = [
    delegate_to_detector,
    delegate_to_reporter,
    delegate_to_translator,
    escalate_to_doctor,
    verify_report_quality,
]


# ─────────────────────────────────────────────────────────────
#  Supervisor agent
# ─────────────────────────────────────────────────────────────
supervisor_agent = create_react_agent(
    model=_supervisor_llm,
    tools=SUPERVISOR_TOOLS,
    prompt=SUPERVISOR_PROMPT,
)


# ─────────────────────────────────────────────────────────────
#  Runner — same interface as before, no changes needed in app.py
# ─────────────────────────────────────────────────────────────
def run_agent(image_path: str, language: str) -> dict:
    """Run the multi-agent supervisor and return structured outputs."""

    user_message = (
        f"Analyze this chest X-ray: {image_path}\n"
        f"Patient language: {language}\n"
        f"Coordinate the specialists and produce the final outputs."
    )

    result = supervisor_agent.invoke(
        {"messages": [{"role": "user", "content": user_message}]},
        config={"recursion_limit": 40},  # higher for multi-agent coordination
    )

    # ---------- Extract structured outputs ----------
    outputs = {
        "findings": None,
        "clinical_report": None,
        "urgency": None,
        "patient_summary": None,
        "escalated": False,
        "agent_trace": [],
        "final_message": None,
    }

    for msg in result["messages"]:
        # Capture tool calls
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            for tc in msg.tool_calls:
                outputs["agent_trace"].append(
                    {
                        "tool": tc["name"],
                        "args": tc["args"],
                    }
                )

        # Capture tool results
        if msg.__class__.__name__ == "ToolMessage":
            tool_name = getattr(msg, "name", "")
            content = msg.content

            if tool_name == "delegate_to_detector":
                outputs["findings"] = content
            elif tool_name == "delegate_to_reporter":
                # Reporter returns both report and urgency — store the whole thing
                outputs["clinical_report"] = content
            elif tool_name == "delegate_to_translator":
                outputs["patient_summary"] = content
            elif tool_name == "escalate_to_doctor":
                outputs["escalated"] = True

    # Extract urgency from the reporter's output (simple heuristic)
    if outputs["clinical_report"]:
        report_lower = str(outputs["clinical_report"]).lower()
        if "critical" in report_lower:
            outputs["urgency"] = "critical"
        elif "urgent" in report_lower:
            outputs["urgency"] = "urgent"
        else:
            outputs["urgency"] = "routine"

    outputs["final_message"] = result["messages"][-1].content

    # ---------- Safety net ----------
    if outputs["clinical_report"] is None and outputs["findings"]:
        from tools import write_clinical_report

        outputs["clinical_report"] = write_clinical_report.invoke(
            {"findings": outputs["findings"]}
        )
    if outputs["urgency"] is None:
        outputs["urgency"] = "routine"
    if outputs["patient_summary"] is None and outputs["clinical_report"]:
        from tools import write_patient_summary

        outputs["patient_summary"] = write_patient_summary.invoke(
            {"report": outputs["clinical_report"], "language": language}
        )

    return outputs
