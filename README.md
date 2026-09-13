# 🩺 MedScribe AI

An agentic radiology assistant that reads chest X-rays, detects abnormalities, explains its reasoning with heatmaps, writes a structured clinical report, and produces a plain-language patient summary in the patient's own language.

---

## ✨ Features

- 🖼️ Chest X-ray analysis with two interchangeable CV models:
  - ResNet18 (fine-tuned, 2-class: NORMAL / PNEUMONIA)
  - DenseNet121 (TorchXRayVision, 18 pathologies)
- 🔥 Grad-CAM heatmaps showing which regions the model focused on
- 🧠 Agentic workflow built with LangGraph — the LLM decides which tools to call, in what order, with self-verification
- 📋 Structured clinical report (findings → impression → recommendation → urgency → reasoning)
- 🚨 Urgency triage (routine / urgent / critical) with auto-escalation for critical findings
- 💬 Patient-friendly summary in English, Urdu, Spanish, Arabic, or Hindi
- 🗂️ Tabbed UI — Upload, Diagnosis, Agent Trace, Patient View, Export
- 📥 Downloadable session record with findings, report, urgency and summary

---

## 🏗️ Architecture

```
User uploads X-ray + picks language
        ↓
AGENT (LangGraph ReAct + openai/gpt-oss-120b via Groq)
        ↓
  decides to call:
    1. detect_findings        → CV model (ResNet18 or DenseNet121)
    2. write_clinical_report  → structured report
    3. assess_urgency         → routine / urgent / critical
    4. escalate_to_doctor     → only if critical
    5. write_patient_summary  → plain language + translation
    6. verify_report_quality  → self-verification
        ↓
Streamlit tabbed UI:
    📤 Upload  |  🩺 Diagnosis  |  🧠 Agent Trace  |  💬 Patient  |  📥 Export
```

---

## 🧰 Tech Stack

| Layer | Tool |
|---|---|
| Frontend | Streamlit (tabbed UI) |
| CV Model (A) | Fine-tuned ResNet18 (2-class) |
| CV Model (B) | TorchXRayVision DenseNet121 |
| Explainability | Grad-CAM |
| Agent Framework | LangGraph (ReAct agent) |
| LLM | openai/gpt-oss-120b via Groq |
| Model Hosting | Hugging Face Hub |
| Language | Python 3.11 |

---

## 📁 Project Structure

```
medscribe-ai/
├── app.py                # Streamlit UI (tabbed layout)
├── orchestrator.py       # LangGraph ReAct agent
├── tools.py              # Agent tools
├── vision.py             # CV models + Grad-CAM
├── agent.py              # LLM report generation helpers
├── report.py             # Output formatting
├── prompts.py            # LLM prompts
├── settings.py           # Config + env + HF repo
├── requirements.txt
├── README.md
├── .env                  # (not committed)
├── models/               # placeholders only
├── samples/              # demo X-rays
└── outputs/              # generated results
```

---

## 🚀 Setup

### 1. Clone & enter

```bash
git clone <your-repo-url>
cd medscribe-ai
```

### 2. Create virtual environment (Python 3.11)

```bash
py -3.11 -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # macOS/Linux
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add your Groq API key

Create a `.env` file:

```
GROQ_API_KEY=your_groq_key_here
```

Get a free key at https://console.groq.com/keys

### 5. Run the app

```bash
streamlit run app.py
```

Open http://localhost:8501

---

## 🧠 Models

### Model A — Fine-tuned ResNet18 (default)

- Backbone: ResNet18 (ImageNet pretrained, final layer fine-tuned)
- Classes: NORMAL, PNEUMONIA
- Weights hosted on Hugging Face Hub → `TabasumDev/medscribe-resnet18`
- Downloaded at runtime on first launch (cached afterwards)

### Model B — DenseNet121 (TorchXRayVision)

- Pretrained on ~224K chest X-rays
- Classes: 18 pathologies
- Loaded by name (`densenet121-res224-all`) — no file upload needed

**Switching models:** set `USE_CUSTOM_MODEL = True/False` at the top of `vision.py`.

---

## 🤖 Agent Design

The agent is a LangGraph ReAct agent powered by `openai/gpt-oss-120b` on Groq. It is semi-autonomous: given a goal and a set of tools, the LLM decides which tools to call and in what order.

The workflow includes:

- Tool selection by the LLM (not hardcoded)
- Self-verification via `verify_report_quality` before finishing
- Conditional escalation — `escalate_to_doctor` is only called if urgency is critical
- Safety net — if the LLM skips a required step, the code fills the gap

The Agent Trace tab in the UI shows exactly which tools the agent decided to call, in order, with inputs.

---

## 🧪 Usage

1. Open the 📤 Upload tab
2. Upload a chest X-ray (JPG/PNG)
3. Select the patient's language
4. Click Run clinical analysis
5. Explore the other tabs:
   - 🩺 Diagnosis — scan, heatmap, urgency badge, findings bars, clinical report
   - 🧠 Agent Trace — every tool the agent decided to call
   - 💬 Patient — plain-language summary in the chosen language
   - 📥 Export — download the full session record

---

## ☁️ Deployment (Streamlit Cloud)

1. Push this repo to GitHub
2. Go to https://share.streamlit.io → New app
3. Select the repo, branch `main`, main file `app.py`
4. In Advanced settings → Secrets, add:

```toml
GROQ_API_KEY = "your_key_here"
```

5. Click Deploy

The ResNet18 weights are downloaded automatically from Hugging Face Hub at runtime and cached by Streamlit Cloud.

---

## ⚠️ Disclaimer

This project is a proof of concept built for a hackathon.
It is not a medical device and must not be used for real clinical diagnosis.
Always consult a qualified radiologist.

---

## 📜 License

MIT