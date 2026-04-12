import os
from dotenv import load_dotenv
from google import genai
from collections import defaultdict
from src.gemini_client import safe_generate

def group_chunks_by_source(chunks: list) -> dict:
    grouped = defaultdict(list)
    for chunk in chunks:
        grouped[chunk["source"]].append(chunk["text"])
    return dict(grouped)


def build_crossref_prompt(query: str, grouped: dict) -> str:
    sources_block = ""
    for source, texts in grouped.items():
        combined = " ".join(texts[:3])  # top 3 chunks per source
        sources_block += f"\n### From: {source}\n{combined}\n"

    return f"""You are a Computer Science academic assistant.

TASK: Answer the question below by synthesizing information across ALL provided sources.

RULES:
- Mention which source contributes what
- Highlight agreements between sources
- Highlight contradictions or gaps if any
- Structure the answer with:
  ## Combined Understanding
  ## Source Contributions
  ## Gaps / Contradictions (if any)

QUESTION:
{query}

SOURCES:
{sources_block}
"""


def cross_reference(query: str, chunks: list) -> dict:
    grouped = group_chunks_by_source(chunks)
    prompt = build_crossref_prompt(query, grouped)

    answer = safe_generate(prompt)
    if not getattr(answer, "text", None):
        raise ValueError("Empty response from Gemini")

    return {
        "answer": answer,
        "sources_used": list(grouped.keys()),
        "source_count": len(grouped),
    }