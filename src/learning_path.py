import os
from dotenv import load_dotenv
from google import genai
from src.gemini_client import safe_generate
STAGES = ["Theory", "Examples", "Practice", "Assessment"]


def build_stage_prompt(topic: str, stage: str, chunks: list) -> str:
    sources_block = ""
    for i, c in enumerate(chunks, 1):
        sources_block += f"\n[Source {i} | {c['source']} | {c['category']}]\n{c['text']}\n"

    instructions = {
        "Theory": (
            "Provide a clear theoretical explanation of the topic.\n"
            "Include: definition, how it works, key terms, and real-world use cases.\n"
            "Use headings. Write for a student seeing this topic for the first time."
        ),
        "Examples": (
            "Provide 2-3 worked examples on this topic.\n"
            "Each example should show: problem → step-by-step solution → result.\n"
            "Use examples from the sources if available, else construct simple ones."
        ),
        "Practice": (
            "Generate 3 practice questions on this topic (varied difficulty).\n"
            "Format:\n"
            "Q1 [Easy]: ...\nQ2 [Medium]: ...\nQ3 [Hard]: ...\n"
            "After each question provide a hint in brackets."
        ),
        "Assessment": (
            "Create a mini assessment with 5 questions:\n"
            "- 2 short answer\n- 2 application\n- 1 analysis/design\n"
            "Include model answers at the end under '## Answer Key'."
        ),
    }

    return f"""You are a Computer Science academic tutor.

LEARNING STAGE: {stage.upper()}
TOPIC: {topic}

TASK:
{instructions[stage]}

RULES:
- Use ONLY the provided sources
- Keep language clear and student-friendly
- Do not skip steps in examples

SOURCES:
{sources_block}
"""


def generate_learning_stage(topic: str, stage: str, chunks: list) -> str:
    prompt = build_stage_prompt(topic, stage, chunks)
    return safe_generate(prompt)
    


def get_all_stages(topic: str, chunks: list) -> dict:
    return {
        stage: generate_learning_stage(topic, stage, chunks)
        for stage in STAGES
    }