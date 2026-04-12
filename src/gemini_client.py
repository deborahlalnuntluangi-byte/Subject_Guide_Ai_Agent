import os
import time
from dotenv import load_dotenv
from google import genai
from openai import OpenAI

load_dotenv()

gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

GEMINI_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
]

OPENAI_MODEL = ["gpt-4o-mini",  # fallback
                "gpt-3.5-turbo"]  # fallback


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
    try:
        response = openai_client.chat.completions.create(
            model=OPENAI_MODEL,
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
        if "insufficient_quota" in err.lower():
            raise RuntimeError(
                "OpenAI quota exhausted. Check billing at platform.openai.com."
            ) from e
        elif "401" in err or "invalid" in err.lower():
            raise RuntimeError(
                "Invalid OpenAI API key. Check your .env file."
            ) from e
        raise RuntimeError(f"OpenAI error: {err}") from e


def safe_generate(prompt: str) -> str:
    # Step 1 — try Gemini first
    try:
        result = try_gemini(prompt)
        return result
    except RuntimeError as e:
        if "gemini_exhausted" not in str(e):
            raise  # non-quota Gemini error, surface it

    # Step 2 — Gemini failed, fall back to OpenAI
    try:
        result = try_openai(prompt)
        return result
    except RuntimeError:
        raise  # OpenAI also failed, surface its error

    # Step 3 — both failed
    raise RuntimeError(
        "Both Gemini and OpenAI are unavailable. Try again in a few minutes."
    )