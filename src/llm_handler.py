# llm_handler.py
import os
from dotenv import load_dotenv
from src.gemini_client import safe_generate  # ← use shared client

load_dotenv()


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
        base_style = """
- Answer in table format
- Give at least 5 to 10 comparison points
- Add a short summary after the table
"""
    elif question_type == "definition":
        base_style = """
- Start with a clear definition
- Then explain in simple words
- Add one small example if possible
- End with a short conclusion
"""
    elif question_type == "long":
        base_style = """
- Give a detailed answer with headings
- Include definition, explanation, example, and conclusion
"""
    elif question_type == "lab":
        base_style = """
- Write like a lab record
- Use headings such as Aim, Theory, Procedure, Result
"""
    else:
        base_style = """
- Give a clear structured explanation
- Include definition, explanation, example, and conclusion wherever possible
"""

    if mode == "Exam Mode":
        style = """
Write the answer in exam-friendly format.
- Use headings and subheadings
- Explain properly
- Keep it clear and neat
- For long answers, make it suitable for 5 to 10 marks
""" + base_style
    else:
        style = """
Write the answer in short and direct format.
- Keep it simple
- Avoid unnecessary detail
- Still maintain clarity
""" + base_style

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
- Use only the given context
- Follow the order of questions exactly
- Do not change the order
- Do not repeat the same point
- Do not duplicate sections
- Keep the answer relevant to the asked question
- Use simple academic English
- If the context is limited, answer only from the available content and do not invent extra facts

IF MULTIPLE PARTS:
- Answer in this format:
## Part 1
## Part 2
## Part 3
- Keep the same order as the question

IF COMPARISON QUESTION:
- Must use table format
- Must include 5 to 10 comparison points
- Add a short concluding sentence after the table

STYLE INSTRUCTIONS:
{style}

QUESTION:
{question_block}

CONTEXT:
{context}
"""

    response_text = safe_generate(prompt).strip()
    response_text = response_text.replace("\n\n\n", "\n\n")

    return response_text