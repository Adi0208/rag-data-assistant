"""
check_models.py
Lists all Gemini models available for your API key.

Usage:
    python backend/check_models.py
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

print("\n✅ Generative models (for chat/SQL):\n")
for m in genai.list_models():
    if "generateContent" in m.supported_generation_methods:
        print(f"  {m.name}")

print("\n✅ Embedding models (for RAG):\n")
for m in genai.list_models():
    if "embedContent" in m.supported_generation_methods:
        print(f"  {m.name}")