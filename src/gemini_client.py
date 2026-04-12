import os
import time
from dotenv import load_dotenv
from google import genai

load_dotenv()

gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Only initialize OpenAI if key exists
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai_client = None
if OPENAI_API_KEY:
    from openai import OpenAI
    openai_client = OpenAI(api_key=OPENAI_API_KEY)

GEMINI_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
]

OPENAI_MODELS = [
    "gpt-4o-mini",
    "gpt-3.5-turbo",
]


def try_gemini(prompt: str) -> str:
    last_error = None
    RETRYABLE = ["429", "503", "404", "RESOURCE_EXHAUSTED", "NOT_FOUND", "UNAVAILABLE"]

    for i, model in enumerate(GEMINI_MODELS):
        try:
            response = gemini_client.models.generate_content(
                model=model,
                contents=prompt
            )
            if getattr(response, "text", None):
                return response.text.strip()
        except Exception as e:
            err = str(e)
            if any(code in err for code in RETRYABLE):
                last_error = e
                if i < len(GEMINI_MODELS) - 1:
                    time.sleep(2)
                continue
            raise

    raise RuntimeError("gemini_exhausted") from last_error


def try_openai(prompt: str) -> str:
    if not openai_client:
        raise RuntimeError("OpenAI key not configured.")

    last_error = None

    for i, model in enumerate(OPENAI_MODELS):  # ← now iterates properly
        try:
            response = openai_client.chat.completions.create(
                model=model,  # ← string not list
                messages=[
                    {
                        "role": "system",
                        "content": "You are a Computer Science academic assistant."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=2048,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()

        except Exception as e:
            err = str(e)
            if "insufficient_quota" in err.lower() or "429" in err:
                last_error = e
                if i < len(OPENAI_MODELS) - 1:
                    time.sleep(2)
                continue
            elif "401" in err or "invalid" in err.lower():
                raise RuntimeError(
                    "Invalid OpenAI API key. Check your Streamlit secrets."
                ) from e
            raise RuntimeError(f"OpenAI error: {err}") from e

    raise RuntimeError("All OpenAI models quota exhausted.") from last_error


def safe_generate(prompt: str) -> str:
    # Step 1 — try Gemini first
    try:
        return try_gemini(prompt)
    except RuntimeError as e:
        if "gemini_exhausted" not in str(e):
            raise

    # Step 2 — fall back to OpenAI if available
    if openai_client:
        return try_openai(prompt)

    # Step 3 — both unavailable
    raise RuntimeError(
        "Gemini quota exhausted and no OpenAI key configured. Try again later."
    )