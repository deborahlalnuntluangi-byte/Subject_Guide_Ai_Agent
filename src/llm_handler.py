import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

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

    # Decide base style
    if question_type == "definition":
        base_style = "Start with a clear definition."
    elif question_type == "long":
        base_style = "Give a detailed explanation."
    elif question_type == "lab":
        base_style = "Explain step-by-step like a lab record."
    elif question_type == "comparison":
        base_style = "Answer in a clear table format with at least 5–10 comparison points."
    else:
        base_style = "Give a clear structured explanation."

    # Adjust using mode
    if mode == "Exam Mode":
        style = base_style + " Give full detailed answer with headings."
    else:
        style = base_style + " Keep the answer short and direct."

    # Multi-question detection
    if "?" in query and len(query.split("?")) > 1:
        multi_question = True
    else:
        multi_question = False

    extra_instruction = ""

    if multi_question:
        extra_instruction = """
    Split the answer like this:

    ## Part 1
    (answer first question)

    ## Part 2
    (answer second question)
    """
    prompt = f"""
You are a Computer Science academic assistant.

STRICT INSTRUCTIONS:
- Do NOT repeat content
- Do NOT duplicate sections
- Answer clearly and only once
- Use only the provided context

IMPORTANT:
- If the question contains multiple parts:
    → Answer each part separately
    → Use clear headings for each part

- If the question is a comparison:
    → MUST present answer in TABLE format
    → Include at least 5–10 points

STYLE:
{style}

QUESTION:
{query}

CONTEXT:
{context}
"""

    # API call
    import time

    max_retries = 3

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )

            response_text = response.text.strip()
            response_text = response_text.replace("\n\n\n", "\n\n")

            return response_text

        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2)  # wait 2 seconds and retry
            else:
                return "⚠️ AI service is currently busy. Please try again in a few seconds."