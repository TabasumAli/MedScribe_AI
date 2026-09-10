# 🩺 MedScribe AI

An agentic radiology assistant that reads chest X-rays, detects abnormalities, explains its reasoning with heatmaps, writes a structured clinical report, and produces a plain-language patient summary in the patient's own language.

---

## ✨ Features

- 🖼️ Chest X-ray analysis using a pretrained DenseNet121 model (18 pathologies)
- 🔥 Grad-CAM heatmap showing where the AI looked
- 📋 Structured clinical report (findings → impression → recommendation → urgency)
- 🚨 Urgency triage (routine / urgent / critical)
- 💬 Patient-friendly summary in English, Urdu, Spanish, Arabic, or Hindi
- 🧠 Agentic workflow powered by Llama 3.3 70B via Groq

---

## 🏗️ Architecture

User uploads X-ray + picks language
        ↓
DenseNet121 (TorchXRayVision) → detects abnormalities + confidence
        ↓
Grad-CAM → heatmap of AI attention
        ↓
Llama 3.3 70B (Groq) → clinical report + urgency + patient summary
        ↓
Streamlit UI → shows image, heatmap, report, urgency badge, translated summary

---

## 🧰 Tech Stack

| Layer | Tool |
|---|---|
| Frontend | Streamlit |
| CV Model | TorchXRayVision (densenet121-res224-all) |
| Explainability | Grad-CAM |
| LLM | Llama 3.3 70B via Groq |
| Language | Python 3.11 |

---

## 📁 Project Structure

medscribe-ai/
├── app.py              # Streamlit UI
├── vision.py           # CV model + heatmap
├── agent.py            # LLM report generation
├── report.py           # Output formatting
├── prompts.py          # LLM prompts
├── settings.py         # Config + env loading
├── requirements.txt
├── .env                # (not committed)
├── samples/            # Demo X-rays
└── outputs/            # Generated results

---

## 🚀 Setup

### 1. Clone & enter
git clone <your-repo-url>
cd medscribe-ai

### 2. Create virtual environment (Python 3.11)
py -3.11 -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # macOS/Linux

### 3. Install dependencies
pip install -r requirements.txt

### 4. Add your Groq API key
Create a .env file:
GROQ_API_KEY=your_groq_key_here

Get a free key at https://console.groq.com/keys

### 5. Run the app
streamlit run app.py

Open http://localhost:8501

---

## 🧪 Usage

1. Upload a chest X-ray (JPG/PNG)
2. Select the patient's language
3. Click Analyze
4. View:
   - Original scan + Grad-CAM heatmap
   - Clinical report
   - Detected findings with confidence
   - Urgency badge
   - Patient summary in chosen language

---

## ⚠️ Disclaimer

This project is a proof of concept built for a hackathon.
It is not a medical device and must not be used for real clinical diagnosis.
Always consult a qualified radiologist.

---

## 📜 License

MIT