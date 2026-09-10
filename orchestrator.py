from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq
from settings import GROQ_API_KEY, LLM_MODEL
from tools import TOOLS

llm = ChatGroq(
    api_key=GROQ_API_KEY,
    model=LLM_MODEL,
    temperature=0.2,
)

SYSTEM_PROMPT = """You are MedScribe AI, an agentic radiology assistant.

Your job: analyze a chest X-ray and produce a complete report for the radiologist.

You have these tools:
- detect_findings: runs the CV model on the image
- write_clinical_report: generates the structured clinical report
- assess_urgency: classifies urgency as routine / urgent / critical
- write_patient_summary: creates a plain-language patient summary in their language
- escalate_to_doctor: sends an urgent alert (use ONLY when urgency is critical)

Workflow:
1. ALWAYS call detect_findings first with the given image path.
2. Then call write_clinical_report with the findings.
3. Then call assess_urgency on the report.
4. If urgency is critical, call escalate_to_doctor with a short reason.
5. Finally call write_patient_summary with the report and the target language.

Think step by step. Call tools in the right order. Do not skip steps.
When done, respond with a final JSON-like summary of what you did.
"""

agent = create_react_agent(
    model=llm,
    tools=TOOLS,
    prompt=SYSTEM_PROMPT,
)

def run_agent(image_path: str, language: str) -> dict:
    """Runs the full agentic pipeline and returns the collected outputs."""
    user_message = (
        f"Analyze this chest X-ray: {image_path}\n"
        f"Patient language: {language}\n"
        f"Follow the workflow exactly."
    )

    result = agent.invoke({
        "messages": [{"role": "user", "content": user_message}]
    })

    # Extract tool outputs from the agent's message history
    outputs = {
        "findings": None,
        "clinical_report": None,
        "urgency": None,
        "patient_summary": None,
        "escalated": False,
        "agent_trace": [],
    }

    for msg in result["messages"]:
        # Capture tool calls and results
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            for tc in msg.tool_calls:
                outputs["agent_trace"].append({
                    "tool": tc["name"],
                    "args": tc["args"],
                })
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

    outputs["final_message"] = result["messages"][-1].content
    return outputs