import os
import time
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def safe_generate(prompt):
    for _ in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            return response.text
        except Exception:
            time.sleep(2)

    return "⚠️ AI service is currently busy. Please try again in a few seconds."


def generate_answer(query, retrieved_chunks, question_type="general", mode="Exam Mode"):
    context_parts = []

    for i, chunk in enumerate(retrieved_chunks, start=1):
        context_parts.append(
            f"""[Source {i}]
File: {chunk['source']}
Category: {chunk['category']}
Content: {chunk['text']}"""
        )

    context = "\n\n".join(context_parts)

    if question_type == "comparison":
        base_style = "Answer in a clear table format with at least 5–10 comparison points."
    elif question_type == "definition":
        base_style = "Start with a clear definition."
    elif question_type == "long":
        base_style = "Give a detailed explanation."
    elif question_type == "lab":
        base_style = "Explain step-by-step like a lab record."
    else:
        base_style = "Give a clear structured explanation."

    if mode == "Exam Mode":
        style = base_style + " Give full detailed answer with headings."
    else:
        style = base_style + " Keep the answer short and direct."

    questions = [q.strip() for q in query.split("?") if q.strip()]
    multi_question = len(questions) > 1

    if multi_question:
        formatted_questions = ""
        for i, q in enumerate(questions, start=1):
            formatted_questions += f"Part {i}: {q}\n"
        question_block = formatted_questions
    else:
        question_block = query

    prompt = f"""
You are a Computer Science academic assistant.

STRICT INSTRUCTIONS:
- Follow the order of questions EXACTLY as given
- Do NOT change order
- Do NOT repeat content
- Do NOT duplicate sections
- Answer clearly and only once
- Use only the provided context
- Use citations, but mention each source only once per section if possible

If multiple parts:
- Answer as:
## Part 1
## Part 2
... in the same order

If comparison:
- MUST use table format
- Include at least 5–10 comparison points

STYLE:
{style}

QUESTION:
{question_block}

CONTEXT:
{context}
"""

    response_text = safe_generate(prompt).strip()
    response_text = response_text.replace("\n\n\n", "\n\n")

    return response_text