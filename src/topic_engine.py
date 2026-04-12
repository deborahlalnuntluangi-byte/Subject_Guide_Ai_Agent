import os
from dotenv import load_dotenv
from google import genai
from src.gemini_client import safe_generate



def build_topic_prompt(query: str, chunks: list, mode: str) -> str:
    sources_block = ""
    for i, c in enumerate(chunks, 1):
        sources_block += f"\n[Source {i} | {c['source']} | {c['category']}]\n{c['text']}\n"

    style = (
        "Write a detailed academic explanation with:\n"
        "- Definition\n- Key concepts with headings\n"
        "- Real examples\n- Summary\nSuitable for 10-mark exam answer."
        if mode == "Exam Mode"
        else
        "Write a short, clear explanation. Bullet points where helpful. "
        "Skip unnecessary detail."
    )

    return f"""You are a Computer Science academic assistant.

TASK: Explain the topic asked below using ONLY the provided sources.

STYLE:
{style}

STRICT RULES:
- Use only the given sources
- Do not invent facts
- Cite source numbers like [1], [2] where relevant
- If topic spans multiple sources, combine them coherently

QUESTION:
{query}

SOURCES:
{sources_block}
"""


def explain_topic(query: str, chunks: list, mode: str = "Exam Mode") -> str:
    prompt = build_topic_prompt(query, chunks, mode)
    return safe_generate(prompt)