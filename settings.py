# import os
# from dotenv import load_dotenv

# load_dotenv()

# GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# LLM_MODEL = "openai/gpt-oss-120b"
# SUPPORTED_LANGUAGES = ["English", "Urdu"]

# settings.py
import os
from dotenv import load_dotenv

load_dotenv()

def get_secret(key):
    try:
        import streamlit as st
        return st.secrets.get(key, os.getenv(key))
    except Exception:
        return os.getenv(key)

GROQ_API_KEY = get_secret("GROQ_API_KEY")
LLM_MODEL = "openai/gpt-oss-120b"
SUPPORTED_LANGUAGES = ["English", "Urdu"]
OUTPUT_DIR = "/tmp/outputs" if os.path.exists("/tmp") and os.access("/tmp", os.W_OK) else "outputs"

# Hugging Face model repo — for downloading weights at runtime
HF_MODEL_REPO = "TabasumDev/medscribe-resnet18"
HF_MODEL_FILENAME = "medscribe_model_a_resnet18.pth"