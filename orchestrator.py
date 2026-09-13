# orchestrator.py
from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq
from settings import GROQ_API_KEY, LLM_MODEL
from tools import TOOLS


# ═══════════════════════════════════════════════════════════════
#  LLM — low temperature for consistent autonomous reasoning
# ═══════════════════════════════════════════════════════════════
llm = ChatGroq(
    api_key=GROQ_API_KEY,
    model=LLM_MODEL,
    temperature=0.1,   # lowered from 0.2 for more consistent tool-calling
)


# ═══════════════════════════════════════════════════════════════
#  SYSTEM PROMPT — goal-only, no hardcoded workflow
#  The LLM decides which tools to call and in what order.
# ═══════════════════════════════════════════════════════════════
SYSTEM_PROMPT = """You are MedScribe AI, an autonomous radiology agent.

YOUR GOAL: Analyze the chest X-ray at the given path and produce:
1. A structured clinical report for the radiologist
2. A plain-language patient summary in the patient's target language
3. An escalation alert to the on-call doctor IF the findings are critical

YOU HAVE FULL AUTONOMY over which tools to call and in what order.
Available tools:
- detect_findings: runs the CV model on the image
- write_clinical_report: generates the structured clinical report
- assess_urgency: classifies urgency as routine / urgent / critical
- write_patient_summary: creates a plain-language patient summary in the given language
- escalate_to_doctor: sends an urgent alert — use ONLY if urgency is critical

Think step by step. Decide what to do next based on what you've learned 
so far from previous tool calls. Explain your reasoning between tool calls.
When the goal is complete, summarize what you did and why.

Do not stop halfway. If a tool returns an error, adjust your approach.
"""


# ═══════════════════════════════════════════════════════════════
#  AGENT — LangGraph ReAct loop with the tools
# ═══════════════════════════════════════════════════════════════
agent = create_react_agent(
    model=llm,
    tools=TOOLS,
    prompt=SYSTEM_PROMPT,
)


# ═══════════════════════════════════════════════════════════════
#  RUNNER — invoke agent, collect outputs, return structured dict
# ═══════════════════════════════════════════════════════════════
def run_agent(image_path: str, language: str) -> dict:
    """Run the autonomous agent and return the collected outputs."""

    user_message = (
        f"Analyze this chest X-ray: {image_path}\n"
        f"Patient language: {language}\n"
        f"You decide the best approach."
    )

    result = agent.invoke(
        {"messages": [{"role": "user", "content": user_message}]},
        config={"recursion_limit": 30},   # allow more tool-call iterations
    )

    # ---------- Extract structured outputs from message history ----------
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
        # Capture tool calls and their arguments
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            for tc in msg.tool_calls:
                outputs["agent_trace"].append({
                    "tool": tc["name"],
                    "args": tc["args"],
                })

        # Capture tool results
        if msg.__class__.__name__ == "ToolMessage":
            tool_name = getattr(msg, "name", "")
            content = msg.content

            if tool_name == "detect_findings":
                outputs["findings"] = content
            elif tool_name == "write_clinical_report":
                outputs["clinical_report"] = content
            elif tool_name == "assess_urgency":
                outputs["urgency"] = content
            elif tool_name == "write_patient_summary":
                outputs["patient_summary"] = content
            elif tool_name == "escalate_to_doctor":
                outputs["escalated"] = True

    # Final message from the agent
    outputs["final_message"] = result["messages"][-1].content

    # ---------- Fallback: if agent forgot a step, fill critical gaps ----------
    # (safety net — keeps the app functional even if the LLM skips a tool)
    if outputs["clinical_report"] is None and outputs["findings"]:
        # write_clinical_report was skipped — call it directly
        from tools import write_clinical_report
        outputs["clinical_report"] = write_clinical_report.invoke(
            {"findings": outputs["findings"]}
        )

    if outputs["urgency"] is None and outputs["clinical_report"]:
        from tools import assess_urgency
        outputs["urgency"] = assess_urgency.invoke(
            {"report": outputs["clinical_report"]}
        )

    if outputs["patient_summary"] is None and outputs["clinical_report"]:
        from tools import write_patient_summary
        outputs["patient_summary"] = write_patient_summary.invoke(
            {"report": outputs["clinical_report"], "language": language}
        )

    return outputs