import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODELS_TO_TEST = [
    "gemini-2.5-flash",
    "gemini-2.5-flash-preview-04-17",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-1.5-flash",
    "gemini-1.5-flash-8b",
    "gemini-1.5-pro",
]

for model in MODELS_TO_TEST:
    try:
        response = client.models.generate_content(
            model=model,
            contents="Say hello in one word"
        )
        print(f"✅ {model} → {response.text.strip()}")
    except Exception as e:
        err = str(e)[:80]
        print(f"❌ {model} → {err}")